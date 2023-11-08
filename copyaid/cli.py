from .core import make_openai_request, LiveOpenAiApi, Config
from .diff import diffadapt

# Python standard libraries
import argparse, json, os
from datetime import datetime
from pathlib import Path
from warnings import warn
from typing import Optional, Union

COPYAID_TMP_DIR = ("TMPDIR", "copyaid")
COPYAID_CONFIG_FILE = ("XDG_CONFIG_HOME", "copyaid/copyaid.toml")
COPYAID_LOG_DIR = ("XDG_STATE_HOME", "copyaid/log")
QOAI_DEFAULT_SET_FILE = ("XDG_CONFIG_HOME", "qoai/set/default")

STD_BASE_DIRS = dict(
    TMPDIR="/tmp",
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)


def get_std_path(env_var_name: str, subpath) -> Path:
    base_dir = os.environ.get(env_var_name)
    if base_dir is None:
        base_dir = STD_BASE_DIRS[env_var_name]
    return Path(base_dir).expanduser() / subpath


def log_openai_query(name, request, response, log_format):
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


def write_revisions(outpath_pattern, source, revisions):
    revisions = diffadapt(source, revisions)
    for i, out_text in enumerate(revisions):
        path = Path(outpath_pattern.format(i + 1))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as file:
            file.write(out_text)


class Main:
    def __init__(self, cmd_line_args: Optional[list[str]] = None):
        parser = argparse.ArgumentParser(description="Query OpenAI")
        parser.add_argument("sources", type=Path, nargs="+")
        parser.add_argument("-s", "--set", type=Path)
        parser.add_argument("--dest", type=Path, default=".")
        parser.add_argument("-c", "--config", type=Path)
        args = parser.parse_args(cmd_line_args)

        self.sources: list[Path] = args.sources
        self.set: Optional[Path] = args.set
        self.dest: Optional[Path] = args.dest
        if args.config is None:
            args.config = Path(get_std_path(*COPYAID_CONFIG_FILE))
        assert isinstance(args.config, Path)
        self.config = Config(args.config)
        self.api = LiveOpenAiApi(self.config.api_key_path())

    def do_file(self, src_path: Path) -> None:
        outpath = str(self.dest) + "/R{}/" + src_path.name
        if Path(outpath.format(1)).exists():
            print("Already exists", outpath.format(1))
        else:
            print("OpenAI query for", src_path)
            with open(src_path) as file:
                source_text = file.read()
            request = make_openai_request(self.set, source_text)
            response = self.api.query(request)
            log_openai_query(src_path.stem, request, response, self.config.log_format)
            print("Writing", outpath.format("*"))
            revisions = list()
            for choice in response.get("choices", []):
                text = choice.get("message", {}).get("content")
                revisions.append(text)
            write_revisions(outpath, source_text, revisions)

    def run(self) -> int:
        if self.set is None:
            self.set = get_std_path(*QOAI_DEFAULT_SET_FILE)
        for s in self.sources:
            self.do_file(s)
        return 0


def main(cmd_line_args: Optional[list[str]] = None) -> int:
    return Main(cmd_line_args).run()
