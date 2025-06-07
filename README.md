# Swarm Simulation

This repository contains a simple Python program that simulates a swarm of red dots on a black background. The user can place a single flag by clicking the mouse, and the dots will attempt to move toward that flag. Only one red dot can occupy a pixel at any time.

## Requirements

- Python 3
- [Pygame](https://www.pygame.org/)
- [pyenv](https://github.com/pyenv/pyenv) with [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

Dependencies install automatically via `run.sh`, but pyenv and pyenv-virtualenv
must be installed and initialized in your shell. If you encounter an error about
`pyenv activate` not being available, ensure you have run:

```bash
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

## Running

Execute the simulation using the provided helper script:

```bash
./run.sh
```

Click anywhere in the window to place the target flag for the swarm.
