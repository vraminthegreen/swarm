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

Control groups allow commands to target subsets of your army. Groups are
numbered from `1` to `9`; by default footmen are in group `1` and archers in
group `2`. Use the numeric keys `1` and `2` to select the active group.

Commands are issued using the mouse or hotkeys:

- Left click or press `A` to place an attack flag, replacing the current queue.
- Hold `Shift` while clicking or pressing `A` to append an attack flag instead.
- Press `M` to place a fast-move flag that clears the queue.
- Hold `Shift` with `M` to append a fast-move flag.

Press the `Delete` key to remove the most recently queued flag for the active
group and `Backspace` to clear that group's queue. Clicking a flag along its path
removes only that flag. A dashed line shows the planned path from each control
group to its queued flags so you can see orders for all groups at a glance. The
simulation updates about 10 times per second and displays a small flag instead of
a green square. Each control group also shows a small banner at its center of
mass with the group number, making it easier to identify footmen and archer
groups during battle.

## Gameplay

Footmen attack the closest enemy within `ATTACK_RANGE` pixels (default `12`).
Their attacks kill the target with a probability defined by the swarm's
`kill_probability` parameter (default `0.02`). Archers behave differently: they
can attack from `ARCHER_ATTACK_RANGE` pixels (60 by default) but with a reduced
kill chance set via their own `kill_probability` value (one third of the
footman value). Defeated ants are removed from the simulation.
