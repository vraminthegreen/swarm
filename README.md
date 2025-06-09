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

Use the `1`, `2`, `3` and `4` keys to choose which red flag is active. The icons for the
four flags are shown at the bottom of the window. The active flag is highlighted
with a rectangle. Control groups allow commands to target subsets of your army.
Groups are numbered from `1` to `9`; by default footmen are in group `1` and
archers in group `2`. Flag 1 controls only group `1`, flag 2 controls only group
`2`, flag 3 orders units to move quickly (speed ×1.5) and disables their attacks,
and flag 4 tells ants to stay put while still allowing them to attack. Click
anywhere to append a new command to the selected group's queue. Each control group
maintains its own list of commands executed in the order they were added. Press the
`Delete` key to remove the most recently queued flag for the active group. Press
`Backspace` to clear that group's queue. A dashed line shows the planned path from the
targeted control group to each flag in its queue. The simulation
updates about 10 times per second and displays a small flag instead of a green
square.
Each control group also shows a small banner at its center of mass with the
group number, making it easier to identify footmen and archer groups during
battle.

## Gameplay

Footmen attack the closest enemy within `ATTACK_RANGE` pixels (default `12`).
Their attacks kill the target with probability defined by `KILL_PROBABILITY`
(default `0.02`). Archers behave differently: they can attack from
`ARCHER_ATTACK_RANGE` pixels (60 by default) but with a reduced kill chance of
`ARCHER_KILL_PROBABILITY` (one third of the footman value). Defeated ants are
removed from the simulation.
