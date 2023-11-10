from .util import get_std_path, copy_package_file
from .core import ApiProxy, Config, Task

# Python standard libraries
import argparse
from sys import stderr
from pathlib import Path
from typing import Optional

COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILENAME = "copyaid.toml"
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/" + COPYAID_CONFIG_FILENAME)
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")


def main(cmd_line_args: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="CopyAid", prog="copyaid")
    parser.add_argument("-c", "--config", type=Path)
    (args, rest) = parser.parse_known_args(cmd_line_args)

    if args.config is None:
        args.config = Path(get_std_path(*COPYAID_CONFIG_FILE))
    elif args.config.is_dir():
        args.config = args.config / COPYAID_CONFIG_FILENAME
    assert isinstance(args.config, Path)
    if not args.config.exists():
        if rest == ["init"]:
            copy_package_file(COPYAID_CONFIG_FILENAME, args.config)
            copy_package_file("cold-revise.toml", args.config.parent)
            return 0
        else:
            msg = "Config file '{}' not found, run:\n  {} --config '{}' init\n"
            stderr.write(msg.format(args.config, parser.prog, args.config))
            return 1

    config = Config(args.config)
    parser.add_argument("task", choices=config.task_names)
    parser.add_argument("-d", "--dest", type=Path)
    parser.add_argument("source", type=Path, nargs="+")
    parser.parse_args(cmd_line_args, args)

    if args.dest is None:
        args.dest = Path(get_std_path(*COPYAID_TMP_DIR))
    task = Task(args.dest, config.get_task(args.task))
    if task.settings is not None:
        api = ApiProxy(config, get_std_path(*COPYAID_LOG_DIR))
        for s in args.source:
            print("OpenAI query for", s)
            revisions = api.do_request(task.settings, s)
            print("Writing to", task.dest)
            task.write_revisions(s, revisions)
    for s in args.source:
        task.do_react(s)
    return 0
