import os
import re
import argparse
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure logging to file in the script's directory"""
    log_file = os.path.join(os.getcwd(), 'copyright_updater.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def log_file_status(file_path, status, message=None):
    """Log file processing status"""
    log_message = f"{status.ljust(8)} {file_path}"
    if message:
        log_message += f" - {message}"
    logging.info(log_message)

def load_config():
    """Load and validate configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing config.json: {e}")
        raise SystemExit(1)

    required_keys = ['headers', 'extensions', 'shbang_patterns', 
                    'exclude_dirs', 'copyright_text']
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required configuration key: {key}")
            raise SystemExit(1)

    return config

def generate_header(language, config):
    """Generate copyright header for a given language"""
    headers = config['headers'].get(language)
    if not headers:
        return None
        
    prefix = headers.get('prefix', '').rstrip()
    suffix = headers.get('suffix', '').lstrip()
    copyright_text = config['copyright_text']
    
    # Create header with dynamic decoration length
    copyright_line = f"{prefix} {copyright_text} {suffix}".strip()
    line_length = max(len(copyright_line), 60)
    decorative_line = f"{prefix}{'-' * (line_length - len(prefix) - len(suffix))}{suffix}"
    
    return (
        f"{decorative_line}\n"
        f"{copyright_line}\n"
        f"{decorative_line}\n\n"
    )

def get_language(file_path, config):
    """Determine language from extension or shebang line"""
    ext = os.path.splitext(file_path)[1][1:].lower()
    language = config['extensions'].get(ext)
    
    if not language:
        try:
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    shebang = first_line[2:].split()[0]
                    for lang, pattern in config['shbang_patterns'].items():
                        if pattern in shebang:
                            return lang
        except Exception as e:
            logging.warning(f"Error reading {file_path}: {e}")
    
    return language

def check_existing_copyright(content, config):
    """Check if copyright text exists in the first 10 lines"""
    copyright_text = config['copyright_text']
    lines = content.split('\n')[:10]
    return any(copyright_text in line for line in lines)

def is_text_file(file_path):
    """Check if a file is a text file using the 'file' command"""
    try:
        result = subprocess.run(
            ['file', '--mime-type', '-b', file_path],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip().startswith('text/')
    except subprocess.CalledProcessError as e:
        logging.warning(f"Error checking MIME type for {file_path}: {e}")
        return False

def main():
    setup_logging()
    logging.info("=== Copyright Header Update Process Started ===")
    
    config = load_config()
    parser = argparse.ArgumentParser(description='Add copyright headers to files.')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('run_mode', nargs='?', default='dryrun',
                       help="Run mode: 'dryrun' or 'update'")
    args = parser.parse_args()

    root_dir = args.directory
    dry_run = args.run_mode.lower() == 'update'

    if not os.path.isdir(root_dir):
        logging.error(f"Invalid directory: {root_dir}")
        raise SystemExit(1)

    exclude_dirs = set(config['exclude_dirs'])
    processed_files = 0
    updated_files = 0
    passed_files = 0
    error_files = 0
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            processed_files += 1
            
            try:
                if not is_text_file(file_path):
                    log_file_status(file_path, "SKIPPED", "Non-text file")
                    continue

                language = get_language(file_path, config)
                if not language:
                    log_file_status(file_path, "SKIPPED", "Unsupported type")
                    continue

                header = generate_header(language, config)
                if not header:
                    log_file_status(file_path, "SKIPPED", "No header format")
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if check_existing_copyright(content, config):
                    log_file_status(file_path, "PASSED")
                    passed_files += 1
                    continue

                shebang_line = None
                rest_content = content
                
                if content.startswith('#!'):
                    lines = content.split('\n', 1)
                    shebang_line = lines[0]
                    rest_content = lines[1] if len(lines) > 1 else ''

                if dry_run:
                    log_file_status(file_path, "DRY_RUN")
                else:
                    original_mode = os.stat(file_path).st_mode
                    with tempfile.NamedTemporaryFile(
                        mode='w', 
                        delete=False, 
                        encoding='utf-8',
                        dir=os.path.dirname(file_path)
                    ) as tmp_file:
                        if shebang_line:
                            tmp_file.write(f"{shebang_line}\n\n")
                        tmp_file.write(header)
                        tmp_file.write(rest_content)
                    
                    os.chmod(tmp_file.name, original_mode)
                    os.replace(tmp_file.name, file_path)
                    log_file_status(file_path, "UPDATED")
                    updated_files += 1

            except Exception as e:
                error_files += 1
                log_file_status(file_path, "ERROR", str(e))
                if 'tmp_file' in locals() and os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)

    logging.info("\n=== Processing Summary ===")
    logging.info(f"Total files processed: {processed_files}")
    logging.info(f"Files updated:         {updated_files}")
    logging.info(f"Files passed:          {passed_files}")
    logging.info(f"Files with errors:     {error_files}")
    logging.info("=== Process Completed ===")

if __name__ == '__main__':
    main()
