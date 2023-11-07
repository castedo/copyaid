from .core import make_openai_request, live_query_openai, get_xdg_path
from .diff import diffadapt

# Python standard libraries
import argparse, json, os
from datetime import datetime
from pathlib import Path

QOAI_DEFAULT_SET_FILE = ("XDG_CONFIG_HOME", "qoai/set/default")
QOAI_LOG_DIR = ("XDG_STATE_HOME", "qoai/log")


def log_openai_query(name, request, response, log_path):
    t = datetime.utcfromtimestamp(response["created"])
    ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
    data = dict(request=request, response=response)
    if log_path is None:
        log_path = get_xdg_path(*QOAI_LOG_DIR)
        os.makedirs(log_path, exist_ok=True)
    save_stem = name + "." + ts
    print("Saving OpenAI response", save_stem)
    try:
        import jsoml  # type: ignore

        jsoml.dump(data, log_path / (save_stem + ".xml"))
    except ImportError:
        with open(log_path / (save_stem + ".json"), "w") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.write("\n")


def write_revisions(outpath_pattern, source, revisions):
    revisions = diffadapt(source, revisions)
    for i, out_text in enumerate(revisions):
        path = Path(outpath_pattern.format(i + 1))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as file:
            file.write(out_text)


def do_file(src_path, settings, outdir, log):
    outpath = str(outdir) + "/R{}/" + src_path.name
    if Path(outpath.format(1)).exists():
        print("Already exists", outpath.format(1))
    else:
        print("OpenAI query for", src_path)
        with open(src_path) as file:
            source_text = file.read()
        request = make_openai_request(settings, source_text)
        response = live_query_openai(request)
        log_openai_query(src_path.stem, request, response, log)
        print("Writing", outpath.format("*"))
        revisions = list()
        for choice in response["choices"]:
            text = choice["text"] if "text" in choice else choice["message"]["content"]
            revisions.append(text)
        write_revisions(outpath, source_text, revisions)


class Main:
    def __init__(self, cmd_line_args = None):
        parser = argparse.ArgumentParser(description="Query OpenAI")
        parser.add_argument("sources", type=Path, nargs="+")
        parser.add_argument("-s", "--set", type=Path)
        parser.add_argument("--dest", type=Path, default=".")
        parser.add_argument("--log", type=Path)
        parser.parse_args(cmd_line_args, self)

    def run(self):
        if self.set is None:
            self.set = get_xdg_path(*QOAI_DEFAULT_SET_FILE)
        for s in self.sources:
            do_file(s, self.set, self.dest, self.log)
        return 0

def main(cmd_line_args = None):
    return Main(cmd_line_args).run()
