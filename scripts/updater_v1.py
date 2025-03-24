#!/usr/bin/env python3
"""
Copyright Header Updater v1.1 (YAML Config)
"""
import os
import re
import argparse
import subprocess
import tempfile
import yaml  # Changed from json
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Configure logging with timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(os.getcwd(), f'copyright_updater_{timestamp}.log')
    
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
    
    logging.info(f"Log file: {log_file}")

def load_config():
    """Load and validate configuration from config.yaml"""
    config_path = Path(__file__).parent / "config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {config_path}")
        raise SystemExit(1)
    except yaml.YAMLError as e:
        logging.error(f"Error parsing config.yaml: {e}")
        raise SystemExit(1)

    required_keys = ['headers', 'extensions', 'shbang_patterns', 
                    'exclude_dirs', 'copyright_text']
    for key in required_keys:
        if key not in config:
            logging.error(f"Missing required configuration key: {key}")
            raise SystemExit(1)

    return config

# [Rest of your existing functions remain unchanged...]

def main():
    setup_logging()
    logging.info("=== Copyright Header Update Process Started ===")
    
    config = load_config()  # Now loads from YAML
    parser = argparse.ArgumentParser(description='Add copyright headers to files.')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('run_mode', nargs='?', default='dryrun',
                       choices=['dryrun', 'update'],
                       help="Run mode: 'dryrun' or 'update'")
    args = parser.parse_args()

    # [Rest of your main() implementation...]

if __name__ == '__main__':
    main()
