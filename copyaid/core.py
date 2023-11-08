# Python Standard Library
import json
from pathlib import Path

import openai
import toml  # type: ignore
from typing import Optional


class LiveOpenAiApi:
    def __init__(self, api_key_path: Optional[Path] = None):
        if api_key_path is not None:
            with open(api_key_path, 'r') as file:
                openai.api_key = file.read().strip()

    def query(self, req: dict) -> dict:
        return openai.ChatCompletion.create(**req)


def read_settings_file(settings_path: Path) -> dict:
    with open(settings_path, 'rb') as file:
        if settings_path.suffix == ".json":
            return json.load(file)
        try:
            return json.load(file)
        except json.JSONDecodeError:
            pass
    import jsoml
    ret = jsoml.load(settings_path)
    if not isinstance(ret, dict):
        raise SyntaxError("CopyAId settings file XML root must be <obj>")
    return ret


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


class Config:
    def __init__(self, config_file: Path):
        self._file_path = config_file if config_file.exists() else None
        if self._file_path:
            with open(self._file_path, "r") as f:
                self._data = dict(toml.load(f))
        else:
            self._data = dict()

    def api_key_path(self) -> Optional[Path]:
        ret = None
        if self._file_path:
            s = self._data.get("openai_api_key_file")
            if s is not None:
                ret = Path(str(s)).expanduser()
                if not ret.is_absolute():
                    ret = self._file_path.parent / ret
        return ret

    @property
    def log_format(self):
        return self._data.get("log_format")
