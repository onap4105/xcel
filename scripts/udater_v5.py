#!/usr/bin/env python3
"""
Copyright Header Updater v1.5

KEY FEATURES:
================================================
1. AUTOMATED HEADER MANAGEMENT:
   - Adds/updates copyright headers in source files
   - Supports multiple file types (Python, Java, Shell, etc.)
   - Preserves existing headers to avoid duplicates

2. INTELLIGENT LANGUAGE DETECTION:
   - Prioritizes shbang line (#!) over file extensions
   - Handles complex cases:
     * Versioned interpreters (python3.12, perl5, etc.)
     * env-style invocations (/usr/bin/env)
     * Multiple components in shbang lines
   - Sorted pattern matching (longest-first) for accuracy

3. SAFE OPERATION MODES:
   - Dry-run mode (default): Preview changes without modification
   - Update mode: Apply changes to files
   - Atomic writes with permission preservation

4. COMPREHENSIVE LOGGING:
   - Timestamped log files
   - Separate log for unsupported files (-s flag)
   - Detailed processing summary

5. FLEXIBLE CONFIGURATION:
   - YAML-based configuration (config.yaml)
   - Customizable:
     * Header formats per language
     * File extension mappings
     * Shbang patterns
     * Excluded directories
   - Supports version-specific variants (python2/python3)

6. ROBUST ERROR HANDLING:
   - Graceful handling of permission issues
   - Skip non-text files
   - Comprehensive error logging

7. ENHANCED SHBANG PROCESSING:
   - Extracts all possible language identifiers
   - Handles special cases:
     * /usr/bin/env python3.12
     * /bin/bash -e
     * Versioned interpreters

USAGE:
================================================
Basic:      copyright_updater.py [DIRECTORY] [dryrun|update]
With logs:  copyright_updater.py [DIRECTORY] update -s

CONFIGURATION:
================================================
Edit config.yaml to:
- Add new file types
- Modify header formats
- Update shbang patterns
- Adjust excluded directories
"""

import os
import re
import argparse
import subprocess
import tempfile
import sys
from typing import Dict, Any, Optional, Set, List, Tuple
import yaml
import logging
from pathlib import Path
from datetime import datetime

def setup_logging(config_dir: Path, unsupported_log: bool = False) -> None:
    """Configure logging with timestamped filenames."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    main_log = config_dir / f'copyright_updater_{timestamp}.log'
    
    logging.basicConfig(
        filename=str(main_log),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    if unsupported_log:
        unsupported_logfile = config_dir / f'unsupported_files_{timestamp}.log'
        unsupported_handler = logging.FileHandler(str(unsupported_logfile))
        unsupported_handler.setLevel(logging.WARNING)
        unsupported_handler.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger('unsupported').addHandler(unsupported_handler)
    
    logging.info("Main log file: %s", main_log)
    if unsupported_log:
        logging.info("Unsupported files log: %s", unsupported_logfile)

def load_config() -> Tuple[Dict[str, Any], List[Tuple[str, str]]]:
    """Load and validate configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as ex:
        logging.error("Configuration file not found at %s", config_path)
        sys.exit(1)
    except yaml.YAMLError as ex:
        logging.error("Error parsing config.yaml: %s", ex)
        sys.exit(1)

    required_keys = {'headers', 'extensions', 'shbang_patterns', 
                   'exclude_dirs', 'copyright_text'}
    missing_keys = required_keys - set(config.keys())
    if missing_keys:
        logging.error("Missing required configuration keys: %s", ", ".join(missing_keys))
        sys.exit(1)

    # Create sorted shbang patterns (longest first)
    shbang_patterns = sorted(
        config['shbang_patterns'].items(),
        key=lambda x: (-len(x[1]), x[1])
    )
    
    return config, shbang_patterns

def generate_header(language: str, config: Dict[str, Any]) -> Optional[str]:
    """Generate copyright header for a given language."""
    headers = config['headers'].get(language)
    if not headers:
        return None
        
    prefix = headers.get('prefix', '').rstrip()
    suffix = headers.get('suffix', '').lstrip()
    copyright_text = config['copyright_text']
    
    copyright_line = f"{prefix} {copyright_text} {suffix}".strip()
    line_length = max(len(copyright_line), 60)
    decorative_line = f"{prefix}{'-' * (line_length - len(prefix) - len(suffix))}{suffix}"
    
    return f"{decorative_line}\n{copyright_line}\n{decorative_line}\n\n"

def extract_shbang_components(shbang_line: str) -> List[str]:
    """Extract all possible language components from a shbang line."""
    # Remove #! and split into components
    parts = shbang_line[2:].strip().split()
    if not parts:
        return []
    
    # Get the interpreter path
    interpreter = parts[0]
    
    # Extract all possible language identifiers
    components = []
    
    # 1. Full interpreter name (e.g., /usr/bin/python3.12)
    components.append(os.path.basename(interpreter))
    
    # 2. Split version numbers (python3.12 -> python3, python)
    if '.' in components[-1]:
        base = components[-1].split('.')[0]
        components.append(base)
        if base[-1].isdigit():  # python3 -> python
            components.append(base.rstrip('0123456789'))
    
    # 3. env-style (env python3)
    if len(parts) > 1 and parts[0].endswith('/env'):
        components.extend(parts[1:])
    
    # Clean components (lowercase, alphanumeric only)
    clean_components = []
    for component in components:
        clean = re.sub(r'[^a-zA-Z0-9]', '', component.lower())
        if clean:
            clean_components.append(clean)
    
    return list(set(clean_components))  # Remove duplicates

def get_language(file_path: Path, config: Dict[str, Any], 
                shbang_patterns: List[Tuple[str, str]]) -> Optional[str]:
    """
    Determine language from shbang line first (with enhanced detection),
    then fall back to extension.
    """
    # First check for shbang line
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!'):
                components = extract_shbang_components(first_line)
                
                # Check patterns in order (longest first)
                for lang, pattern in shbang_patterns:
                    clean_pattern = re.sub(r'[^a-zA-Z0-9]', '', pattern.lower())
                    if clean_pattern in components:
                        return lang
    except Exception as ex:
        logging.getLogger('unsupported').warning("%s - Read error: %s", file_path, ex)
        return None

    # Fall back to extension if shbang check failed
    ext = file_path.suffix[1:].lower()
    return config['extensions'].get(ext)

def check_existing_copyright(content: str, config: Dict[str, Any]) -> bool:
    """Check if copyright text exists in the first 10 lines."""
    copyright_text = config['copyright_text']
    lines = content.split('\n')[:10]
    return any(copyright_text in line for line in lines)

def is_text_file(file_path: Path) -> bool:
    """Check if a file is a text file using the 'file' command."""
    try:
        result = subprocess.run(
            ['file', '--mime-type', '-b', str(file_path)],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().startswith('text/')
    except subprocess.CalledProcessError as ex:
        logging.getLogger('unsupported').warning("%s - File type detection failed: %s", file_path, ex)
        return False

def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Add copyright headers to files.')
    parser.add_argument('directory', type=str, help='Directory to process')
    parser.add_argument('run_mode', nargs='?', default='dryrun',
                      choices=['dryrun', 'update'],
                      help="Run mode: 'dryrun' or 'update'")
    parser.add_argument("-s", "--unsupported-log", 
                      action='store_true',
                      help="Create separate log for unsupported files")
    args = parser.parse_args()

    config_dir = Path(__file__).parent
    setup_logging(config_dir, args.unsupported_log)
    logging.info("=== Copyright Header Update Process Started ===")
    
    config, shbang_patterns = load_config()
    root_dir = Path(args.directory)
    dry_run = args.run_mode.lower() != 'update'

    if not root_dir.is_dir():
        logging.error("Invalid directory: %s", root_dir)
        sys.exit(1)

    exclude_dirs = set(config['exclude_dirs'])
    stats = {'processed': 0, 'updated': 0, 'passed': 0, 'errors': 0}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            stats['processed'] += 1
            
            try:
                process_file(file_path, config, dry_run, stats, shbang_patterns)
            except Exception as ex:
                stats['errors'] += 1
                logging.error("%s - ERROR - %s", file_path, ex)

    logging.info("\n=== Processing Summary ===")
    logging.info("Total files processed: %d", stats['processed'])
    logging.info("Files updated:         %d", stats['updated'])
    logging.info("Files passed:          %d", stats['passed'])
    logging.info("Files with errors:     %d", stats['errors'])
    logging.info("=== Process Completed ===")

def process_file(file_path: Path, config: Dict[str, Any], dry_run: bool, 
                stats: Dict[str, int], shbang_patterns: List[Tuple[str, str]]) -> None:
    """Process individual file with copyright header updates."""
    if not is_text_file(file_path):
        logging.info("%s - SKIPPED - Non-text file", file_path)
        return

    language = get_language(file_path, config, shbang_patterns)
    if not language:
        logging.info("%s - SKIPPED - Unsupported type", file_path)
        return

    header = generate_header(language, config)
    if not header:
        logging.info("%s - SKIPPED - No header format", file_path)
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if check_existing_copyright(content, config):
        logging.info("%s - PASSED", file_path)
        stats['passed'] += 1
        return

    shbang_line, rest_content = parse_shbang(content)
    
    if dry_run:
        logging.info("%s - DRY_RUN", file_path)
    else:
        update_file(file_path, header, shbang_line, rest_content)
        logging.info("%s - UPDATED", file_path)
        stats['updated'] += 1

def parse_shbang(content: str) -> Tuple[Optional[str], str]:
    """Extract shbang line if present."""
    if content.startswith('#!'):
        lines = content.split('\n', 1)
        return lines[0], lines[1] if len(lines) > 1 else ''
    return None, content

def update_file(file_path: Path, header: str, shbang_line: Optional[str], rest_content: str) -> None:
    """Perform atomic file update with permission preservation."""
    original_mode = file_path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        encoding='utf-8',
        dir=str(file_path.parent)
    ) as tmp_file:
        if shbang_line:
            tmp_file.write(f"{shbang_line}\n\n")
        tmp_file.write(header)
        tmp_file.write(rest_content)
    
    tmp_path = Path(tmp_file.name)
    tmp_path.chmod(original_mode)
    tmp_path.replace(file_path)

if __name__ == '__main__':
    main()
