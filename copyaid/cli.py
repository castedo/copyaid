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
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/copyaid.toml")
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")

STD_BASE_DIRS = dict(
    TMPDIR="/tmp",
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)


def get_std_path(env_var_name: str, subpath: str) -> Path:
    base_dir = os.environ.get(env_var_name)
    if base_dir is None:
        base_dir = STD_BASE_DIRS[env_var_name]
    return Path(base_dir).expanduser() / subpath


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


class Main:
    def __init__(self, cmd_line_args: Optional[list[str]] = None):
        parser = argparse.ArgumentParser(description="CopyAid")
        parser.add_argument("task")
        parser.add_argument("sources", type=Path, nargs="+")
        parser.add_argument("-d", "--dest", type=Path)
        parser.add_argument("-c", "--config", type=Path)
        args = parser.parse_args(cmd_line_args)

        self.sources: list[Path] = args.sources
        self.task: str = args.task
        self.dest: Path = args.dest or Path(get_std_path(*COPYAID_TMP_DIR))
        if args.config is None:
            args.config = Path(get_std_path(*COPYAID_CONFIG_FILE))
        assert isinstance(args.config, Path)
        self.config = Config(args.config)
        self.api = LiveOpenAiApi(self.config.api_key_path())

    def _rev_paths(self, src_path: Path) -> list[Path]:
        ret = list()
        pattern = str(self.dest) + "/R{}/" + src_path.name
        for i in range(MAX_NUM_REVS):
            ret.append(Path(pattern.format(i + 1)))
        return ret

    def do_file(self, settings: Any, src_path: Path) -> None:
        print("OpenAI query for", src_path)
        with open(src_path) as file:
            source_text = file.read()
        request = make_openai_request(settings, source_text)
        response = self.api.query(request)
        log_openai_query(src_path.stem, request, response, self.config.log_format)
        print("Writing to", self.dest)
        revisions = list()
        for choice in response.get("choices", []):
            text = choice.get("message", {}).get("content")
            revisions.append(text)
        write_revisions(self._rev_paths(src_path), source_text, revisions)

    def do_after(self, after_cmd: str, src_path: Path) -> None:
        found_revs = [str(p) for p in self._rev_paths(src_path) if p.exists()]
        if found_revs:
            cmdline = " ".join([after_cmd, str(src_path)] + found_revs)
            subprocess.run(cmdline, check=True, shell=True)

    def run(self) -> int:
        task = self.config.get_task(self.task)
        if task is None:
            msg = "Task '{}' not found in config '{}'"
            print(msg.format(self.task, self.config.path), file=stderr)
            return 1
        (settings, after) = task
        if settings is not None:
            num_revs = settings.get("n", 1)
            if num_revs > MAX_NUM_REVS:
                settings["n"] = MAX_NUM_REVS
                msg = "{} revisions requested, changed to max {}"
                warn(msg.format(num_revs, MAX_NUM_REVS))
            for s in self.sources:
                    self.do_file(settings, s)
        if after is not None:
            for s in self.sources:
                self.do_after(after, s)    
        return 0


def main(cmd_line_args: Optional[list[str]] = None) -> int:
    return Main(cmd_line_args).run()
