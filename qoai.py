#!/usr/bin/python3

QOAI_OPENAI_API_KEY_FILE = ("XDG_CONFIG_HOME", "qoai/openai_api_key.txt")
QOAI_DEFAULT_SET_FILE = ("XDG_CONFIG_HOME", "qoai/set/default")
QOAI_LOG_DIR = ("XDG_STATE_HOME", "qoai/log")

XDG_BASE_DIRS = dict(
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)

# Python Standard Library
import argparse, json, os, re, sys
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


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


def make_openai_request(settings_path, source):
    if settings_path.suffix == ".json":
        with open(settings_path) as file:
            settings = json.load(file)
    else:
        import jsoml  # type: ignore

        settings = jsoml.load(settings_path)

    ret = settings["openai"]
    ret["max_tokens"] = int(settings["max_tokens_ratio"] * len(source) / 4)
    ret["prompt"] = settings["prepend"] + source + settings["append"]
    return ret


def log_openai_query(name, request, response, log_path) -> None:
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


def tokenize(pattern, text):
    return [match[0] for match in pattern.finditer(text)]


def diffadapt(orig_text, revisions):
    ret = []
    re_token = re.compile(r"\w+|\W|\n")
    isjunk = lambda x: x == " "
    matcher = SequenceMatcher(isjunk)
    # ... caches detailed information about the second sequence,
    # so if you want to compare one sequence against many sequences,
    # use set_seq2() ...
    orig = tokenize(re_token, orig_text)
    matcher.set_seq2(orig)
    for rev_text in revisions:
        adapted = []
        rev = tokenize(re_token, rev_text)
        matcher.set_seq1(rev)
        # get_opcodes for converting revised text back to orig
        for tag , r1, r2, o1, o2 in matcher.get_opcodes():
            # tag meaning is relative to going from revised text back to orig
            if tag in ['replace', 'insert'] and "\n" in orig[o1:o2]:
                adapted += ["\n"]
            adapted += rev[r1:r2]
        ret.append("".join(adapted))
    return ret


def write_revisions(outpath_pattern, source, revisions):
    texts = []
    try:
        import nltk  # type: ignore

        for rev in revisions:
            lines = nltk.sent_tokenize(rev.lstrip())
            texts.append("\n".join(lines + [""]))
    except ImportError:
        texts = revisions

    revisions = diffadapt(source, texts)
    for i, out_text in enumerate(revisions):
        with open(outpath_pattern.format(i + 1), "w") as file:
            file.write(out_text)


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
        print("OpenAI query for", args.source)
        with open(args.source) as file:
            source = file.read()
        request = make_openai_request(args.set, source)
        response = live_query_openai(request)
        log_openai_query(args.source.stem, request, response, args.log)
        print("Writing", outpath.format("*"))
        revisions = [c["text"] for c in response["choices"]]
        write_revisions(outpath, source, revisions)


if __name__ == "__main__":
    exit(main())
