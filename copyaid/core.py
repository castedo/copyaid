from .diff import diffadapt

import openai
import tomli

# Python Standard Library
import os, json, subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from warnings import warn

from typing import Any, Iterable, Optional


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
    @dataclass
    class Task:
        settings: Any
        react: str

    def __init__(self, config_file: Path):
        with open(config_file, "rb") as file:
            self._data = tomli.load(file)
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

    @property
    def task_names(self) -> Iterable[str]:
        tasks = self._data.get("tasks", {})
        assert isinstance(tasks, dict)
        return tasks.keys()

    def get_task(self, task_name: str) -> Optional[Task]:
        task = self._data.get("tasks", {}).get(task_name)
        if task is None:
            return None
        path = self._resolve_path(task.get("request"))
        if path is None:
            settings = None
        else:
            with open(path, "rb") as file:
                settings = tomli.load(file)
        react = task.get("react")
        if react is not None:
            cmd = self._data.get("commands", {}).get(react)
            if cmd is None:
                msg = f"Command '{react}' not found in {self.path}"
                raise SyntaxError(msg)
            react = cmd
        return Config.Task(settings, react)


class ApiProxy:
    ApiClass = LiveOpenAiApi

    def __init__(self, config: Config, log_path: Path):
        self.log_path = log_path
        self.log_format = config.log_format
        self._api = ApiProxy.ApiClass(config.api_key_path())

    def do_request(self, settings: Any, src_path: Path) -> list[str]:
        with open(src_path) as file:
            source_text = file.read()
        request = make_openai_request(settings, source_text)
        response = self._api.query(request)
        self.log_openai_query(src_path.stem, request, response)
        revisions = list()
        for choice in response.get("choices", []):
            text = choice.get("message", {}).get("content")
            revisions.append(text)
        return diffadapt(source_text, revisions)

    def log_openai_query(self, name: str, request: Any, response: Any) -> None:
        if not self.log_format:
            return
        t = datetime.utcfromtimestamp(response["created"])
        ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
        data = dict(request=request, response=response)
        os.makedirs(self.log_path, exist_ok=True)
        save_stem = name + "." + ts
        print("Logging OpenAI response", save_stem)
        if self.log_format == "jsoml":
            import jsoml
            jsoml.dump(data, self.log_path / (save_stem + ".xml"))
        elif self.log_format == "json":
            with open(self.log_path / (save_stem + ".json"), "w") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.write("\n")
        else:
            warn("Unsupported log format: {}".format(self.log_format))


class Task:
    MAX_NUM_REVS = 7

    def __init__(self, dest: Path, config: Optional[Config.Task]):
        self.dest = dest
        self.settings = config.settings if config else None
        self.react = config.react if config else None
        if self.settings is not None:
            num_revs = self.settings.get("n", 1)
            if num_revs > Task.MAX_NUM_REVS:
                self.settings["n"] = Task.MAX_NUM_REVS
                msg = "{} revisions requested, changed to max {}"
                warn(msg.format(num_revs, Task.MAX_NUM_REVS))

    def _rev_paths(self, src_path: Path) -> list[Path]:
        ret = list()
        pattern = str(self.dest) + "/R{}/" + src_path.name
        for i in range(Task.MAX_NUM_REVS):
            ret.append(Path(pattern.format(i + 1)))
        return ret

    def write_revisions(self, src_path: Path, revisions: list[str]) -> None:
        for i, path in enumerate(self._rev_paths(src_path)):
            if i < len(revisions):
                os.makedirs(path.parent, exist_ok=True)
                with open(path, "w") as file:
                    file.write(revisions[i])
            else:
                path.unlink(missing_ok=True)

    def do_react(self, src_path: Path) -> int:
        ret = 0
        if self.react is not None:
            found_revs = [str(p) for p in self._rev_paths(src_path) if p.exists()]
            if found_revs:
                args = [self.react] + [str(src_path)] + found_revs
                proc = subprocess.run(args, shell=True)
                ret = proc.returncode
        return ret
