from .core import error, WorkFiles
from .task import Config, Task
from .util import get_std_path

# Python standard libraries
import argparse, logging
from pathlib import Path
from typing import Iterable

PROGNAME = "copyaid"
COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILENAME = "copyaid.toml"
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/" + COPYAID_CONFIG_FILENAME)
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")
MAX_NUM_REVS = 7


def get_config_path(cmd_line_args: list[str] | None) -> Path | None:
    preparser = argparse.ArgumentParser(add_help=False)
    preparser.add_argument("-c", "--config", type=Path)
    (args, rest) = preparser.parse_known_args(cmd_line_args)
    if args.config and not args.config.exists():
        error(f"Config file '{args.config}' not found.")
        return None
    ret = args.config or Path(get_std_path(*COPYAID_CONFIG_FILE))
    if ret.is_dir():
        ret = ret / COPYAID_CONFIG_FILENAME
    return ret


def postconfig_argparser(
    task_names: Iterable[str], help_text: str
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
        description="CopyAId",
        epilog=help_text,
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
    parser.add_argument("task", choices=task_names, metavar="<task>")
    parser.add_argument("source", type=Path, nargs="+", metavar="<source>")
    return parser


def main(cmd_line_args: list[str] | None = None) -> int:
    logging.basicConfig()
    tmp_dir = Path(get_std_path(*COPYAID_TMP_DIR))
    config_path = get_config_path(cmd_line_args)
    if not config_path:
        return 2
    default_config = tmp_dir / "package"
    config = Config(default_config , config_path)
    help_text = (
        f"Default config: {default_config}/copyaid.toml\n" +
        f"User config: {config_path}\n\n" +
        config.help()
    )
    parser = postconfig_argparser(config.task_names, help_text)
    args = parser.parse_args(cmd_line_args)
    if args.dest is None:
        args.dest = tmp_dir
    exit_code = check_filename_collision(args.source)
    if exit_code != 0:
        return exit_code
    task = config.get_task(args.task, get_std_path(*COPYAID_LOG_DIR))
    for src in args.source:
        if not src.exists():
            error(f"File not found: '{src}'")
            exit_code = 2
            break
        work = WorkFiles(src, str(args.dest) + "/R{}/" + src.name, MAX_NUM_REVS)
        exit_code |= do_work(task, work)
        if exit_code > 1:
            break
    return exit_code


def check_filename_collision(sources: list[Path]) -> int:
    filenames = set()
    for s in sources:
        if s.name in filenames:
            msg = "Sources must have unique filenames. Conflict: {}"
            error(msg.format(s.name))
            return 2
        filenames.add(s.name)
    return 0


def do_work(task: Task, work: WorkFiles) -> int:
    if task.can_request:
        print("Saving revisions to", work.dest_glob)
        print(" for source", work.src)
        task.request(work)
    return task.react(work)
