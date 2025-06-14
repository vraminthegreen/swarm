#!/usr/bin/env bash
set -e

ENV_NAME="swarm-env"

if ! command -v pyenv >/dev/null; then
  echo "pyenv is required but not installed. Please install pyenv first." >&2
  exit 1
fi

# Initialize pyenv and pyenv-virtualenv in this shell
export PYENV_ROOT="$(pyenv root)"
eval "$(pyenv init -)"
if command -v pyenv-virtualenv-init >/dev/null; then
  eval "$(pyenv virtualenv-init -)"
else
  echo "pyenv-virtualenv is required but not installed." >&2
  exit 1
fi

# Create virtualenv if it does not exist
if ! pyenv versions --bare | grep -qx "$ENV_NAME"; then
  PYTHON_VERSION="$(pyenv global)"
  pyenv virtualenv "$PYTHON_VERSION" "$ENV_NAME"
fi

pyenv activate "$ENV_NAME"

# Install dependencies
pip install --upgrade pip >/dev/null
pip install pygame >/dev/null
pip install numpy >/dev/null

# Run the game
python main.py
