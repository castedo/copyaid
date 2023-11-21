from .core import ApiProxy
from .task import Config, Task
from .util import get_std_path, copy_package_file

# Python standard libraries
import argparse
from pathlib import Path
from sys import stderr
from typing import Optional, Union

COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILENAME = "copyaid.toml"
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/" + COPYAID_CONFIG_FILENAME)
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")


def preparse_config(prog: str, cmd_line_args: Optional[list[str]]) -> Union[int, Path]:
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument("-c", "--config", type=Path)
    (args, rest) = preparser.parse_known_args(cmd_line_args)
    config_path = args.config or Path(get_std_path(*COPYAID_CONFIG_FILE))
    if config_path.is_dir():
        config_path = config_path / COPYAID_CONFIG_FILENAME
    if not config_path.exists():
        if rest == ["init"]:
            copy_package_file(COPYAID_CONFIG_FILENAME, config_path)
            copy_package_file("cold-example.toml", config_path.parent)
            copy_package_file("warm-example.toml", config_path.parent)
            copy_package_file("proof-example.toml", config_path.parent)
            return 0
        else:
            print(f"Config file '{config_path}' not found, run:", file=stderr)
            if args.config is None:
                print(f"  {prog} init", file=stderr)
            else:
                print(f"  {prog} --config '{args.config}' init", file=stderr)
            return 2
    return config_path


def main(cmd_line_args: Optional[list[str]] = None) -> int:
    prog = "copyaid"
    ret = preparse_config(prog, cmd_line_args)
    if isinstance(ret, int):
        return ret
    config = Config(ret)
    parser = argparse.ArgumentParser(
        prog=prog,
        description="CopyAId",
        epilog=config.help(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c",
        "--config",
        default=argparse.SUPPRESS,
        metavar="<config>",
        help="Configuration file"
    )
    parser.add_argument(
        "-d",
        "--dest",
        type=Path,
        metavar="<dest>",
        help="Destination directory for revisions"
    )
    parser.add_argument("task", choices=config.task_names, metavar="<task>")
    parser.add_argument("source", type=Path, nargs="+", metavar="<source>")
    args = parser.parse_args(cmd_line_args)
    if args.dest is None:
        args.dest = Path(get_std_path(*COPYAID_TMP_DIR))
    ret = check_filename_collision(args.source)
    if ret == 0:
        ret = do_task(config, args.task, args.source, args.dest)
    return ret


def check_filename_collision(sources: list[Path]) -> int:
    filenames = set()
    for s in sources:
        if s.name in filenames:
            msg = "Sources must have unique filenames. Conflict: {}"
            print(msg.format(s.name), file=stderr)
            return 2
        filenames.add(s.name)
    return 0


def do_task(config: Config, task_name: str, sources: list[Path], dest: Path) -> int:
    exit_code = 0
    task = Task(dest, config, task_name)
    if task.settings is None:
        api = None
    else:
        api = config.get_api_proxy(get_std_path(*COPYAID_LOG_DIR))
    for s in sources:
        if not s.exists():
            print(f"File not found: '{s}'", file=stderr)
            exit_code = 2
            break
        if api:
            saved = task.use_saved_revision(s)
            if saved:
                print("Reusing saved", saved)
            else:
                print("OpenAI request for", s)
                revisions = api.do_request(task.settings, s)
                print("Saving to", task.rev_dest_glob(s))
                task.write_revisions(s, revisions)
        exit_code |= task.do_react(s)
        if exit_code > 1:
            break
    return exit_code
