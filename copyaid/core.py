# Python Standard Library
import json
from pathlib import Path

import openai
import tomli
from typing import Any, Optional


class LiveOpenAiApi:
    def __init__(self, api_key_path: Optional[Path] = None):
        if api_key_path is not None:
            with open(api_key_path, 'r') as file:
                openai.api_key = file.read().strip()

    def query(self, req: Any) -> Any:
        return openai.ChatCompletion.create(**req)  # type: ignore


def make_openai_request(settings: Any, source: str) -> Any:
    ret = settings["openai"]
    ret["max_tokens"] = int(settings["max_tokens_ratio"] * len(source) / 4)
    prompt = settings.get("prepend", "") + source + settings.get("append", "")
    ret["messages"] = [
        {
            "role": "system",
            "content": settings["chat_system"]
        },
        {
            "role": "user",
            "content": prompt
        },
    ]
    return ret


class Config:
    def __init__(self, config_file: Path):
        if config_file.exists():
            with open(config_file, "rb") as file:
                self._data = tomli.load(file)
        else:
            self._data = dict()
        self.path = config_file

    def _resolve_path(self, s: Any) -> Optional[Path]:
        ret = None
        if s is not None:
            ret = Path(str(s)).expanduser()
            if not ret.is_absolute():
                ret = self.path.parent / ret
        return ret

    def api_key_path(self) -> Optional[Path]:
        s = self._data.get("openai_api_key_file")
        return self._resolve_path(s)

    @property
    def log_format(self) -> Optional[str]:
        return self._data.get("log_format")

    def get_task(self, task_name: str) -> Optional[tuple[Any, str]]:
        task = self._data.get("tasks", {}).get(task_name)
        if task is None:
            return None
        path = self._resolve_path(task.get("request"))
        if path is None:
            settings = None
        else:
            with open(path, "rb") as file:
                settings = tomli.load(file)
        return (settings, task.get("after"))
