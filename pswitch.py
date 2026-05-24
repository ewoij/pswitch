#!/usr/bin/env python3

import re
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict


DATA_FILE = Path.home() / ".config/pswitch/config.json"


def list_(args: list[str]):
    argsd = to_args_dict(args)
    data = Data.load()
    assert data.depth > 0, 'depth > 0 please'
    dirs = set(iter_dirs(data.dir, data.depth))
    to_hide = argsd.get('hide', [])
    to_hide = [to_hide] if not isinstance(to_hide, list) else to_hide
    to_hide = [Path(v) for v in to_hide if v]
    to_hide = [v if v.is_absolute() else data.dir / v for v in to_hide]
    dirs = dirs - set(to_hide)
    dirs = sorted(dirs)
    ordering = {k: i for i, k in enumerate(data.ordering)}
    dirs = sorted(dirs, key=lambda p: ordering.get(p, len(dirs)))
    for dir_ in dirs:
        print(dir_.relative_to(data.dir) if 'relative' in argsd else dir_)


def top(args: list[str]):
    assert len(args) == 1, '<path> please'
    dir_ = Path(args[0])
    assert dir_.is_dir(), 'not a dir'
    assert dir_.is_absolute(), 'absolute please'
    data = Data.load()
    data.ordering = [dir_] + data.ordering
    data.ordering = list(dict.fromkeys(data.ordering)) # dedup
    data.save()


def config_set(args: list[str]):
    argsd = to_args_dict(args)
    Data(**{**vars(Data.load()), **argsd}).save()
    config_get([])


def config_get(args: list[str]):
    argsd = to_args_dict(args)
    data = asdict(Data.load())
    unknown_keys = [v for v in argsd if v not in data]
    assert unknown_keys == [], f'unknown: {unknown_keys}, available: {list(data)}'
    data = {k: v for k, v in data.items() if not argsd or k in argsd}
    print_key = len(data) > 1
    key_length = max(len(k) for k in data)
    for k, v in data.items():
        if print_key:
            print(k + ' ' * (key_length - len(k) + 1), end='')
        if isinstance(v, list):
            if print_key:
                print(('\n' + ' ' * (key_length + 1)).join(map(str, v)), end='\n' * 2)
            else:
                print('\n'.join(map(str, v)))
        else:
            print(v)


def main():
    try:
        Data.init()
        dispatch_cmd(sys.argv[1:])
    except AssertionError as e:
        print(e)


@dataclass
class Data:
    ordering: list[Path] = field(default_factory=list)
    dir: Path = Path.home()
    depth: int = 1

    def __post_init__(self) -> None:
        self.ordering = [Path(v) for v in self.ordering]
        self.dir = Path(self.dir)
        self.depth = int(self.depth)

    @classmethod
    def load(cls):
        with DATA_FILE.open() as f:
            return cls(**json.load(f))

    def save(self):
        with DATA_FILE.open(mode='w') as f:
            def convert(v):
                if isinstance(v, Path):
                    v = v.expanduser()
                return str(v)
            json.dump(asdict(self), f, default=convert)

    @classmethod
    def init(cls):
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if DATA_FILE.exists(): return
        cls().save()


def help_():
    h = ''
    h += 'commands:\n'
    h += '\n'.join('  ' + ' '.join(c) for c in get_commands())
    return h


def get_commands():
    return {
        ('list',): list_,
        ('config', 'set'): config_set,
        ('config', 'get'): config_get,
        ('top',): top,
    }


def dispatch_cmd(args: list[str]):
    commands = get_commands()

    command = next((c for c in sorted(commands, key=len, reverse=True) if c == tuple(args[:len(c)])), None)

    if command is None:
        print(help_())
        exit(1)

    commands[command](args[len(command):])


def to_args_dict(args: list[str]) -> dict[str, str | list[str] | None]:
    argsd = {}
    for arg in args:
        arg = arg.removeprefix('--')

        if (match := re.search('=+', arg)):
            key, value = arg[:match.start()], arg[match.end():]
        else:
            key, value = arg, None

        argsd.setdefault(key, [])
        if value is not None:
            argsd[key].append(value)

    return {
        k: None if v == [] else 
        v[0] if len(v) == 1 else 
        v
        for k, v in argsd.items()
    }


def iter_dirs(d: Path, depth: int):
    if depth == 0: return
    for v in d.iterdir():
        if not v.is_dir(): continue
        yield v
        for v in iter_dirs(v, depth-1):
            yield v


if __name__ == "__main__":
    main()
