import tomli
from .core import ApiProxy, PromptSettings, WorkFiles

# Python Standard Library
import io, os, subprocess
from pathlib import Path
from typing import Any, Iterable, Optional
from warnings import warn


class Task:
    def __init__(self, api: ApiProxy, react_cmds: list[str]):
        self.api = api
        self._react = react_cmds
        self.settings: PromptSettings | None = None
        self.clean = False

    @property
    def can_request(self) -> bool:
        return bool(self.settings)

    def request(self, work: WorkFiles) -> None:
        assert self.settings
        revisions = self.api.do_request(self.settings, work.src)
        work.write_revisions(revisions)

    def react(self, work: WorkFiles) -> int:
        ret = 0
        if self._react:
            found_revs = [str(p) for p in work.revisions()]
            if found_revs:
                args = [str(work.src)] + found_revs
                for cmd in self._react:
                    proc = subprocess.run([cmd] + args, shell=True)
                    ret = proc.returncode
                    if ret:
                        break
        return ret


class Config:
    """
    Class for handling user config files (usually `copyaid.toml`).
    """
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

    def get_api_key(self) -> str | None:
        api_key = None
        api_key_path = self._data.get("openai_api_key_file")
        api_key_path = self._resolve_path(api_key_path)
        if api_key_path is not None:
            with open(api_key_path, 'r') as file:
                api_key = file.read().strip()
        return api_key

    @property
    def log_format(self) -> Optional[str]:
        return self._data.get("log_format")

    @property
    def task_names(self) -> Iterable[str]:
        tasks = self._data.get("tasks", {})
        assert isinstance(tasks, dict)
        return tasks.keys()

    def _react_as_commands(self, react: Any) -> list[str]:
        ret = list()
        if react is None:
            react = []
        elif isinstance(react, str):
            react = [react]
        for r in react:
            cmd = self._data.get("commands", {}).get(r)
            if cmd is None:
                msg = f"Command '{r}' not found in {self.path}"
                raise SyntaxError(msg)
            ret.append(cmd)
        return ret

    def get_task(self, task_name: str, log_path: Path) -> Task:
        task = self._data.get("tasks", {}).get(task_name)
        if task is None:
            raise ValueError(f"Invalid task name {task_name}.")
        api = ApiProxy(self.get_api_key(), log_path, self.log_format)
        cmds = self._react_as_commands(task.get("react"))
        ret = Task(api, cmds)
        path = self._resolve_path(task.get("request"))
        if path:
            ret.settings = PromptSettings(path)
            ret.clean = task.get("clean", False)
        return ret

    def help(self) -> str:
        buf = io.StringIO()
        buf.write("task choices:\n")
        for name in self.task_names:
            buf.write("  ")
            buf.write(name)
            buf.write("\n")
            task = self._data["tasks"][name]
            path = self._resolve_path(task.get("request"))
            if path:
                if task.get("clean"):
                    buf.write("    Clean & request: ")
                else:
                    buf.write("    Request: ")
                buf.write(str(path))
                buf.write("\n")
            react = self._react_as_commands(task.get("react"))
            if react:
                buf.write("    React command chain:\n")
                for r in react:
                    buf.write("      ")
                    buf.write(help_example_react(r))
            buf.write("\n")
        return buf.getvalue()


def help_example_react(cmd: str) -> str:
    subs = {
        '"$0"': "<source>",
        '"$1"': "<rev1>",
        '"$@"': "<rev1> ... <revN>",
    }
    for k, v in subs.items():
        cmd = cmd.replace(k, v)
    return cmd + "\n"
