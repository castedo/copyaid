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


class TokenSequenceMatcher:
    def __init__(self, focal_text):
        isjunk = lambda x: x == " "
        self.matcher = SequenceMatcher(isjunk, autojunk=False)
        self.re_token = re.compile(r"\w+|\W|\n")
        self.focus = self.tokenize(focal_text)
        # SequenceMatcher: ... caches detailed information about the second sequence,
        # so if you want to compare one sequence against many sequences,
        # use set_seq2() ...
        self.matcher.set_seq2(self.focus)

    def tokenize(self, text):
        return [match[0] for match in self.re_token.finditer(text)]

    def set_alternative(self, alt_text):
        self.alt = self.tokenize(alt_text)
        self.matcher.set_seq1(self.alt)

    def operations(self):
        """tag meaning is relative to going from alt text to focal text"""

        return (
            (tag, self.alt[a1:a2], self.focus[f1:f2])
            for tag, a1, a2, f1, f2 in self.matcher.get_opcodes()
        )


def diffadapt(orig_text, revisions):
    ret = []
    matcher = TokenSequenceMatcher(orig_text)
    for rev_text in revisions:
        adapted = []
        matcher.set_alternative(rev_text)
        # ops for converting revised text back to orig
        for tag, rev_chunk, orig_chunk in matcher.operations():
            if orig_chunk[0:2] == [".", "\n"] and rev_chunk[0:1] in ([","], [";"]):
                adapted += rev_chunk[0:1]
                adapted += ["\n"]
                del rev_chunk[0:1]
                del orig_chunk[0:2]
            if orig_chunk[0:1] == ["\n"] and rev_chunk[0:1] == [" "]:
                rev_chunk[0] = "\n"
            if "\n" in orig_chunk and not "\n" in rev_chunk:
                if adapted[-1:] == [" "]:
                    adapted[-1] = "\n"
                    adapted += [" "]
                elif rev_chunk[0:2] == [",", " "]:
                    rev_chunk.insert(1, "\n")
                elif adapted[-1:] != ["\n"]:
                    adapted += ["\n"]
            adapted += rev_chunk
        ret.append("".join(adapted))
    return ret


def write_revisions(outpath_pattern, source, revisions):
    revisions = diffadapt(source, revisions)
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
