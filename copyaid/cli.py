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

    config_path = args.config or Path(get_std_path(*COPYAID_CONFIG_FILE))
    if config_path.is_dir():
        config_path = config_path / COPYAID_CONFIG_FILENAME
    if not config_path.exists():
        if rest == ["init"]:
            copy_package_file(COPYAID_CONFIG_FILENAME, config_path)
            copy_package_file("cold-revise.toml", config_path.parent)
            return 0
        else:
            print(f"Config file '{config_path}' not found, run:", file=stderr)
            if args.config is None:
                print(f"  {parser.prog} init", file=stderr)
            else:
                print(f"  {parser.prog} --config '{args.config}' init", file=stderr)
            return 1

    config = Config(config_path)
    parser.add_argument("task", choices=config.task_names)
    parser.add_argument("-d", "--dest", type=Path)
    parser.add_argument("source", type=Path, nargs="+")
    parser.parse_args(cmd_line_args, args)

    if args.dest is None:
        args.dest = Path(get_std_path(*COPYAID_TMP_DIR))
    exit_code = 0
    task = Task(args.dest, config.get_task(args.task))
    if task.settings is None:
        api = None
    else:
        api = ApiProxy(config, get_std_path(*COPYAID_LOG_DIR))
    exit_code = 0
    for s in args.source:
        if api:
            print("OpenAI request for", s)
            revisions = api.do_request(task.settings, s)
            print("Saving to", task.dest)
            task.write_revisions(s, revisions)
        exit_code = task.do_react(s)
        if exit_code:
            break
    return exit_code
