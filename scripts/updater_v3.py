#!/usr/bin/env python3
# pylint: disable=too-many-locals,too-many-branches,too-many-statements
"""
Copyright Header Updater v1.3

Features:
- YAML configuration
- Pylint-compliant code structure
- Type hints
- Better exception handling
"""

import os
import re
import argparse
import subprocess
import tempfile
from typing import Dict, Any, Optional, Set
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

def load_config() -> Dict[str, Any]:
    """Load and validate configuration from config.yaml."""
    config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError as ex:
        logging.error("Configuration file not found at %s", config_path)
        raise SystemExit(1) from ex
    except yaml.YAMLError as ex:
        logging.error("Error parsing config.yaml: %s", ex)
        raise SystemExit(1) from ex

    required_keys = {'headers', 'extensions', 'shbang_patterns', 
                   'exclude_dirs', 'copyright_text'}
    missing_keys = required_keys - set(config.keys())
    if missing_keys:
        logging.error("Missing required configuration keys: %s", ", ".join(missing_keys))
        raise SystemExit(1)

    return config

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

def get_language(file_path: Path, config: Dict[str, Any]) -> Optional[str]:
    """Determine language from extension or shebang line."""
    ext = file_path.suffix[1:].lower()
    language = config['extensions'].get(ext)
    
    if not language:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    shebang = first_line[2:].split()[0]
                    for lang, pattern in config['shbang_patterns'].items():
                        if pattern in shebang:
                            return lang
        except Exception as ex:  # pylint: disable=broad-except
            logging.getLogger('unsupported').warning("%s - Read error: %s", file_path, ex)
            return None
    
    if not language:
        logging.getLogger('unsupported').warning("%s", file_path)
    
    return language

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
    
    config = load_config()
    root_dir = Path(args.directory)
    dry_run = args.run_mode.lower() != 'update'

    if not root_dir.is_dir():
        logging.error("Invalid directory: %s", root_dir)
        raise SystemExit(1)

    exclude_dirs = set(config['exclude_dirs'])
    stats = {'processed': 0, 'updated': 0, 'passed': 0, 'errors': 0}
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            stats['processed'] += 1
            
            try:
                process_file(file_path, config, dry_run, stats)
            except Exception as ex:  # pylint: disable=broad-except
                stats['errors'] += 1
                logging.error("%s - ERROR - %s", file_path, ex)

    logging.info("\n=== Processing Summary ===")
    logging.info("Total files processed: %d", stats['processed'])
    logging.info("Files updated:         %d", stats['updated'])
    logging.info("Files passed:          %d", stats['passed'])
    logging.info("Files with errors:     %d", stats['errors'])
    logging.info("=== Process Completed ===")

def process_file(file_path: Path, config: Dict[str, Any], dry_run: bool, stats: Dict[str, int]) -> None:
    """Process individual file with copyright header updates."""
    if not is_text_file(file_path):
        logging.info("%s - SKIPPED - Non-text file", file_path)
        return

    language = get_language(file_path, config)
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

    shebang_line, rest_content = parse_shebang(content)
    
    if dry_run:
        logging.info("%s - DRY_RUN", file_path)
    else:
        update_file(file_path, header, shebang_line, rest_content)
        logging.info("%s - UPDATED", file_path)
        stats['updated'] += 1

def parse_shebang(content: str) -> tuple:
    """Extract shebang line if present."""
    if content.startswith('#!'):
        lines = content.split('\n', 1)
        return lines[0], lines[1] if len(lines) > 1 else ''
    return None, content

def update_file(file_path: Path, header: str, shebang_line: Optional[str], rest_content: str) -> None:
    """Perform atomic file update with permission preservation."""
    original_mode = file_path.stat().st_mode
    with tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        encoding='utf-8',
        dir=str(file_path.parent)
    ) as tmp_file:
        if shebang_line:
            tmp_file.write(f"{shebang_line}\n\n")
        tmp_file.write(header)
        tmp_file.write(rest_content)
    
    tmp_path = Path(tmp_file.name)
    tmp_path.chmod(original_mode)
    tmp_path.replace(file_path)

if __name__ == '__main__':
    main()

[MASTER]
load-plugins=pylint.extensions.mccabe

[MESSAGES CONTROL]
disable=
    C0114,  # Missing module docstring (covered by our existing docstring)
    C0103,  # Variable name doesn't conform to snake_case
    R0903,  # Too few public methods
    R0913,  # Too many arguments
    R0914,  # Too many local variables
    W1203,  # Use lazy % formatting in logging
    W0703   # Catching too general exception

[FORMAT]
max-line-length=120
indent-string=4

[BASIC]
good-names=
    f,      # Common file handle name
    ex,     # Common exception name
    e,      # Common exception name
    _,      # Unused variable
    tmp,    # Temporary variables
    lang    # Language variable

[DESIGN]
max-args=6
max-locals=15
max-returns=6
max-branches=12

[LOGGING]
logging-modules=logging
