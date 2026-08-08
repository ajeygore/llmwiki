#!/bin/bash
# LLMWiki Bootstrapping wrapper calling setup.py

# Locate the engine folder
ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run python script
python3 "$ENGINE_DIR/setup.py" "$@"
