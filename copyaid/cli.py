from .util import get_std_path, copy_package_file
from .core import make_openai_request, LiveOpenAiApi, Config
from .diff import diffadapt

# Python standard libraries
import argparse, json, os, subprocess
from sys import stderr
from datetime import datetime
from pathlib import Path
from warnings import warn
from typing import Any, Optional, Union

# max number of parallel revisions requested
MAX_NUM_REVS = 7

COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILENAME = "copyaid.toml"
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/" + COPYAID_CONFIG_FILENAME)
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")


def log_openai_query(
    name: str, request: Any, response: Any, log_format: Optional[str]
) -> None:
    if not log_format:
        return
    t = datetime.utcfromtimestamp(response["created"])
    ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
    data = dict(request=request, response=response)
    log_path = get_std_path(*COPYAID_LOG_DIR)
    os.makedirs(log_path, exist_ok=True)
    save_stem = name + "." + ts
    print("Saving OpenAI response", save_stem)
    if log_format == "jsoml":
        import jsoml
        jsoml.dump(data, log_path / (save_stem + ".xml"))
    elif log_format == "json":
        with open(log_path / (save_stem + ".json"), "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write("\n")
    else:
        warn("Unsupported log format: {}".format(log_format))


def write_revisions(rev_paths: list[Path], source: str, revisions: list[str]) -> None:
    revisions = diffadapt(source, revisions)  # type: ignore
    for i, path in enumerate(rev_paths):
        if i < len(revisions):
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w") as file:
                file.write(revisions[i])
        else:
            path.unlink(missing_ok=True)


class CopyAid:
    ApiClass = LiveOpenAiApi

    def __init__(self, config: Config, dest: Path):
        self.config = config
        self.dest = dest
        self._api: Any = None

    def _rev_paths(self, src_path: Path) -> list[Path]:
        ret = list()
        pattern = str(self.dest) + "/R{}/" + src_path.name
        for i in range(MAX_NUM_REVS):
            ret.append(Path(pattern.format(i + 1)))
        return ret

    def do_request(self, settings: Any, src_path: Path) -> None:
        print("OpenAI query for", src_path)
        with open(src_path) as file:
            source_text = file.read()
        request = make_openai_request(settings, source_text)
        if self._api is None:
            self._api = CopyAid.ApiClass(self.config.api_key_path())
        response = self._api.query(request)
        log_openai_query(src_path.stem, request, response, self.config.log_format)
        print("Writing to", self.dest)
        revisions = list()
        for choice in response.get("choices", []):
            text = choice.get("message", {}).get("content")
            revisions.append(text)
        write_revisions(self._rev_paths(src_path), source_text, revisions)

    def do_react(self, cmd: str, src_path: Path) -> None:
        found_revs = [str(p) for p in self._rev_paths(src_path) if p.exists()]
        if found_revs:
            cmdline = " ".join([cmd, str(src_path)] + found_revs)
            subprocess.run(cmdline, check=True, shell=True)


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

    task = config.get_task(args.task)
    if task is None:
        msg = "Task '{}' not found in config '{}'"
        print(msg.format(args.task, config.path), file=stderr)
        return 1
    task.cap_num_rev(MAX_NUM_REVS)

    aid = CopyAid(config, args.dest)
    if task.settings is not None:
        for s in args.source:
            aid.do_request(task.settings, s)
    if task.react is not None:
        for s in args.source:
            aid.do_react(task.react, s)
    return 0
