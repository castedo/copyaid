# Python Standard Library
import json, os
from pathlib import Path


###############################################################################
# Core code to query OpenAI API
###############################################################################

QOAI_OPENAI_API_KEY_FILE = ("XDG_CONFIG_HOME", "qoai/openai_api_key.txt")

XDG_BASE_DIRS = dict(
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)


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
    return openai.ChatCompletion.create(**req)


def read_settings_file(settings_path: Path) -> dict:
    with open(settings_path, 'rb') as file:
        if settings_path.suffix == ".json":
            return json.load(file)
        try:
            return json.load(file)
        except json.JSONDecodeError:
            pass
    import jsoml  # type: ignore
    return jsoml.load(settings_path)


def make_openai_request(settings_path, source):
    settings = read_settings_file(settings_path)
    ret = settings["openai"]
    ret["max_tokens"] = int(settings["max_tokens_ratio"] * len(source) / 4)
    prompt = settings.get("prepend", "") + source + settings.get("append", "")
    ret["messages"] = [
        {"role": "system", "content": settings["chat_system"]},
        {"role": "user", "content": prompt},
    ]
    return ret
