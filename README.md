# Swarm Simulation

This repository contains a simple Python program that simulates two swarms of ants competing over flags. Red ants are controlled by the player while blue ants follow an AI-controlled flag. When a swarm member spots an enemy within range it will attack while still moving at a reduced speed (0.3). Attacks have a small chance to remove the target, introducing a basic combat element.

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

Use the `1` and `2` keys to choose which red flag is active. The icons for the
two flags are shown at the bottom of the window. The active flag is highlighted
with a rectangle. Click anywhere to place the currently active flag. Press the
`Delete` key to remove it. The simulation updates about 10 times per second and
displays a small flag instead of a green square.

## Gameplay

Each ant attacks the closest enemy within `ATTACK_RANGE` pixels (default `7`).
An attack kills the target with probability defined by `KILL_PROBABILITY`
(default `0.02`). Defeated ants are removed from the simulation.
