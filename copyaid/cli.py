from .core import WorkFiles
from .task import Config, Task
from .util import get_std_path, copy_package_file

# Python standard libraries
import argparse
from pathlib import Path
from sys import stderr

PROGNAME = "copyaid"
COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILENAME = "copyaid.toml"
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/" + COPYAID_CONFIG_FILENAME)
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")
MAX_NUM_REVS = 7


class ConfigArgPreparse:
    def __init__(self, cmd_line_args: list[str] | None):
        preparser = argparse.ArgumentParser(add_help=False)
        preparser.add_argument("-c", "--config", type=Path)
        (args, rest) = preparser.parse_known_args(cmd_line_args)
        self.config_arg = args.config
        self.config_path = args.config or Path(get_std_path(*COPYAID_CONFIG_FILE))
        if self.config_path.is_dir():
            self.config_path = self.config_path / COPYAID_CONFIG_FILENAME
        self.init = (rest == ["init"])

    def handle_missing_config(self) -> int:
        if self.init:
            copy_package_file(COPYAID_CONFIG_FILENAME, self.config_path)
            copy_package_file("cold-example.toml", self.config_path.parent)
            copy_package_file("warm-example.toml", self.config_path.parent)
            copy_package_file("proof-example.toml", self.config_path.parent)
            return 0
        else:
            print(f"Config file '{self.config_path}' not found, run:", file=stderr)
            if self.config_arg is None:
                print(f"  {PROGNAME} init", file=stderr)
            else:
                print(f"  {PROGNAME} --config '{self.config_arg}' init", file=stderr)
            return 2


def postconfig_argparser(config: Config) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROGNAME,
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
    return parser


def main(cmd_line_args: list[str] | None = None) -> int:
    prep = ConfigArgPreparse(cmd_line_args)
    if not prep.config_path.exists():
        return prep.handle_missing_config()
    config = Config(prep.config_path)
    parser = postconfig_argparser(config)
    args = parser.parse_args(cmd_line_args)
    if args.dest is None:
        args.dest = Path(get_std_path(*COPYAID_TMP_DIR))
    ret = check_filename_collision(args.source)
    if ret == 0:
        task = config.get_task(args.task, get_std_path(*COPYAID_LOG_DIR))
        for src in args.source:
            if not src.exists():
                print(f"File not found: '{src}'", file=stderr)
                ret = 2
                break
            ret |= do_work(task, src, args.dest)
            if ret > 1:
                    break
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


def do_work(task: Task, src: Path, dest: Path) -> int:
    work = WorkFiles(src, str(dest) + "/R{}/" + src.name, MAX_NUM_REVS)
    if task.settings:
        saved = work.one_revision_equal_to_source()
        if saved and not task.clean:
            print("Reusing saved", saved)
        else:
            print("OpenAI request for", src)
            revisions = task.api.do_request(task.settings, src)
            print("Saving to", work.dest_glob)
            work.write_revisions(revisions)
    return task.do_react(work)
