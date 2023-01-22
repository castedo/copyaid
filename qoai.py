#!/usr/bin/python3

OPENAI_API_KEY_CONFIG_FILE = "~/.config/openai/api_key.txt"

try:
    import nltk
except ImportError:
    pass

try:
    import jsoml
except ImportError:
    pass

# Python Standard Library
import argparse, json, sys
from datetime import datetime
from pathlib import Path


def live_query_openai(req):
    import openai

    if openai.api_key is None:
        key_path = Path(OPENAI_API_KEY_CONFIG_FILE).expanduser()
        with open(key_path) as file:
            openai.api_key = file.read().strip()
    return openai.Completion.create(**req)


def query_openai_by_file(settings_path, source_path, dump_path):
    assert dump_path.is_dir()

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
    t = datetime.utcfromtimestamp(response['created'])
    ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
    data = dict(request=oai_req, response=response)
    save_stem = source_path.stem + "." + ts
    print("Saving OpenAI response", save_stem)
    with open(dump_path / (save_stem + ".json"), 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")
    if 'jsoml' in sys.modules:
        jsoml.dump(data, dump_path / (save_stem + ".xml"))

    return response


def main(cmd_line_args=None):
    parser = argparse.ArgumentParser(description="Query OpenAI")
    parser.add_argument("settings", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("dump", type=Path)
    args = parser.parse_args(cmd_line_args)

    new_suffix = args.source.suffix + ".R{}"
    outpath = str(args.source.with_suffix(new_suffix))

    if Path(outpath.format(1)).exists():
        print("Already exists", outpath.format(1))
    else:
        response = query_openai_by_file(args.settings, args.source, args.dump)
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
