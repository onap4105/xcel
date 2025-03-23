import os
import re
import argparse
import subprocess
import tempfile
import json
from pathlib import Path

def load_config():
    """Load and validate configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"Error: Configuration file not found at {config_path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Error parsing config.json: {e}")

    required_keys = ['headers', 'extensions', 'shbang_patterns', 
                    'exclude_dirs', 'copyright_text']
    for key in required_keys:
        if key not in config:
            raise SystemExit(f"Missing required configuration key: {key}")

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
            print(f"Error reading {file_path}: {e}")
    
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
        print(f"Error checking MIME type for {file_path}: {e}")
        return False

def main():
    config = load_config()
    parser = argparse.ArgumentParser(description='Add copyright headers to files.')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('run_mode', nargs='?', default='dryrun',
                       help="Run mode: 'dryrun' or 'update'")
    args = parser.parse_args()

    root_dir = args.directory
    dry_run = args.run_mode.lower() == 'update'

    if not os.path.isdir(root_dir):
        raise SystemExit(f"Error: {root_dir} is not a valid directory")

    exclude_dirs = set(config['exclude_dirs'])
    
    for root, dirs, files in os.walk(root_dir):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            if not is_text_file(file_path):
                continue

            language = get_language(file_path, config)
            if not language:
                continue

            header = generate_header(language, config)
            if not header:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            if check_existing_copyright(content, config):
                print(f"✓ Copyright exists: {file_path}")
                continue

            # Handle shebang preservation
            shebang_line = None
            rest_content = content
            
            if content.startswith('#!'):
                lines = content.split('\n', 1)
                shebang_line = lines[0]
                rest_content = lines[1] if len(lines) > 1 else ''

            print(f"→ {'Dry run' if not dry_run else 'Updating'} {file_path}")
            
            if dry_run:
                continue

            try:
                # Get original permissions
                original_mode = os.stat(file_path).st_mode

                # Create temporary file in the same directory
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
                
                # Preserve original permissions
                os.chmod(tmp_file.name, original_mode)
                
                # Atomic replacement
                os.replace(tmp_file.name, file_path)

            except Exception as e:
                print(f"Error writing to {file_path}: {e}")
                if os.path.exists(tmp_file.name):
                    os.remove(tmp_file.name)

    print("Process complete!")

if __name__ == '__main__':
    main()
