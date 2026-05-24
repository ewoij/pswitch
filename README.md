# pswitch

Quickly switch projects in tmux. Projects are ordered by most-recently-used (MRU).

[![asciicast](https://asciinema.org/a/FhB5YV7ycjW94WN4.svg)](https://asciinema.org/a/FhB5YV7ycjW94WN4)

## Requirements

- [fzf](https://github.com/junegunn/fzf)
- Python 3.10+
- tmux
- bash

## Install

Symlink `pswitch.py` onto your `PATH`:

```sh
ln -s "$PWD/pswitch.py" /usr/local/bin/pswitch
```

Point pswitch at the directory that contains your projects:

```sh
pswitch config set --dir=~/Documents/projects
```

Add a binding to `~/.tmux.conf` (binds `C-b o`):

```
bind o display-popup -E '<path>/pswitch/tmux.sh'
```

## Configuration

- Change the projects directory:
    ```sh
    pswitch config set --dir=~/Documents/work-projects
    pswitch config set --dir=~/Documents/personal-projects
    ```
- Change how deep to scan for projects (default `1`):
    ```sh
    pswitch config set --depth=2
    ```
