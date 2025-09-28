#!/usr/bin/env python3
"""
Environment variable loader for the comic generator.
Loads environment variables from .env file in the project root.
"""

import os
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file in the project root."""
    # Get the project root directory (parent of anthony_code)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    env_file = project_root / '.env'
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
    else:
        print(f"Warning: .env file not found at {env_file}")
        print("Please create a .env file with your GEMINI_API_KEY")
