#!/usr/bin/python3

QOAI_OPENAI_API_KEY_FILE = ("XDG_CONFIG_HOME", "qoai/openai_api_key.txt")
QOAI_DEFAULT_SET_FILE = ("XDG_CONFIG_HOME", "qoai/set/default")
QOAI_LOG_DIR = ("XDG_STATE_HOME", "qoai/log")

XDG_BASE_DIRS = dict(
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)

try:
    import nltk  # type: ignore
except ImportError:
    pass

try:
    import jsoml  # type: ignore
except ImportError:
    pass

# Python Standard Library
import argparse, json, os, sys
from datetime import datetime
from pathlib import Path


def get_xdg_path(xdg_dir_var: str, subpath) -> Path:
    base_dir = os.environ.get(xdg_dir_var)
    if base_dir is None:
        base_dir = XDG_BASE_DIRS[xdg_dir_var]
    return Path(base_dir).expanduser() / subpath


def live_query_openai(req):
    import openai

    if openai.api_key is None:
        key_path = get_xdg_path(*QOAI_OPENAI_API_KEY_FILE)
        with open(key_path) as file:
            openai.api_key = file.read().strip()
    return openai.Completion.create(**req)


def query_openai_by_file(settings_path, source_path, log_path):

    with open(source_path) as file:
        source = file.read()

    if settings_path.suffix == ".json":
        with open(settings_path) as file:
            settings = json.load(file)
    else:
        import jsoml
        settings = jsoml.load(settings_path)

    oai_req = settings["openai"]
    oai_req["max_tokens"] = int(settings["max_tokens_ratio"] * len(source) / 4)
    oai_req["prompt"] = settings["prepend"] + source + settings["append"]

    print("OpenAI query for", source_path)
    response = live_query_openai(oai_req)
    log_openai_query(source_path, oai_req, response, log_path)
    return response


def log_openai_query(source_path, request, response, log_path) -> None:
    t = datetime.utcfromtimestamp(response['created'])
    ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
    data = dict(request=request, response=response)
    if log_path is None:
        log_path = get_xdg_path(*QOAI_LOG_DIR)
        os.makedirs(log_path, exist_ok=True)
    save_stem = source_path.stem + "." + ts
    print("Saving OpenAI response", save_stem)
    with open(log_path / (save_stem + ".json"), 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")
    if 'jsoml' in sys.modules:
        jsoml.dump(data, log_path / (save_stem + ".xml"))


def main(cmd_line_args=None):
    parser = argparse.ArgumentParser(description="Query OpenAI")
    parser.add_argument("source", type=Path)
    parser.add_argument("--set", type=Path)
    parser.add_argument("--log", type=Path)
    args = parser.parse_args(cmd_line_args)

    new_suffix = args.source.suffix + ".R{}"
    outpath = str(args.source.with_suffix(new_suffix))

    if Path(outpath.format(1)).exists():
        print("Already exists", outpath.format(1))
    else:
        if args.set is None:
            args.set = get_xdg_path(*QOAI_DEFAULT_SET_FILE)
        response = query_openai_by_file(args.set, args.source, args.log)
        print("Writing", outpath.format("*"))
        for i, choice in enumerate(response["choices"]):
            out_text = choice["text"]
            with open(outpath.format(i + 1), "w") as file:
                if "nltk" in sys.modules:
                    for line in nltk.sent_tokenize(out_text.lstrip()):
                        print(line, file=file)
                else:
                    file.write(out_text)


if __name__ == "__main__":
    exit(main())
