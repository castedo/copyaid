import tomli
from .util import copy_package_dir, read_file_text, resolve_path
from .core import (
    ApiProxy, CopybreakSyntax, CopyEditor, SimpleParser, SourceParserProtocol,
    TrivialParser, WorkFiles, warning
)

# Python Standard Library
import io, subprocess
from pathlib import Path
from typing import Any, Iterable, Optional


class Task:
    def __init__(self, ed: CopyEditor, react_cmds: list[str]):
        self._editor = ed
        self._react = react_cmds

    @property
    def can_request(self) -> bool:
        return bool(self._editor) and self._editor.has_instructions

    def request(self, work: WorkFiles) -> None:
        assert self.can_request
        self._editor.revise(work)

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


class PackageConfig:
    """
    Class for handling base configuration from package.
    """

    CONFIG_FILENAME = "copyaid.toml"

    def __init__(self, local_dir: Path):
        copy_package_dir("config", local_dir)
        config_file = local_dir / PackageConfig.CONFIG_FILENAME
        with open(config_file, "rb") as file:
            data = tomli.load(file)
        self._formats = data.get("formats", {})
        self._commands = data.get("commands", {})
        self._tasks: dict[str, Any] = dict()
        self._add_task_data(local_dir, data.get("tasks", {}))

    def _add_task_data(self, config_dir: Path, tasks: dict[str, Any]) -> None:
        for key, task in tasks.items():
            self._tasks[key] = dict(
                request=resolve_path(config_dir, task.get("request")),
                react=task.get("react"),
            )

    def _get_parsers(self) -> list[SourceParserProtocol]:
        ret = list()
        for fname, f in self._formats.items():
            if "copybreak" not in f:
                raise SyntaxError(f"Format '{fname}' table missing 'copybreak' key")
            ret.append(SimpleParser.from_POD(f))
        if not ret:
            warning("No file formats specified in config file.")
        return ret + [TrivialParser()]

    def _react_as_commands(self, react: Any) -> list[str]:
        ret = list()
        if react is None:
            react = []
        elif isinstance(react, str):
            react = [react]
        for r in react:
            cmd = self._commands.get(r)
            if cmd is None:
                msg = f"Command '{r}' not found in configuration"
                raise SyntaxError(msg)
            ret.append(cmd)
        return ret


class Config(PackageConfig):
    """
    Class for handling user config files (usually `copyaid.toml`).
    """
    def __init__(self, tmp_dir: Path, config_file: Path):
        super().__init__(tmp_dir)
        if config_file.exists():
            with open(config_file, "rb") as file:
                data = tomli.load(file)
        else:
            data = {}
        self._formats.update(data.get("formats", {}))
        self._commands.update(data.get("commands", {}))
        self._add_task_data(config_file.parent, data.get("tasks", {}))
        key_path = data.get("openai_api_key_file")
        self.api_key = read_file_text(resolve_path(config_file.parent, key_path))
        self.log_format = data.get("log_format")

    @property
    def task_names(self) -> Iterable[str]:
        return self._tasks.keys()

    def get_task(self, task_name: str, log_path: Path) -> Task:
        task = self._tasks.get(task_name)
        if task is None:
            raise ValueError(f"Invalid task name {task_name}.")
        if "clean" in task:
            warning("Configuration setting 'clean' has been deprecated.")
        api = ApiProxy(self.api_key, log_path, self.log_format)
        ed = CopyEditor(api)
        ed.parsers = self._get_parsers()
        ed.add_off_instruction("off")
        if path := task.get("request"):
            ed.set_instruction("on", path)
            ed.set_init_instruction("on")
        cmds = self._react_as_commands(task.get("react"))
        return Task(ed, cmds)

    def help(self) -> str:
        buf = io.StringIO()
        buf.write("task choices:\n")
        for name in self.task_names:
            buf.write("  ")
            buf.write(name)
            buf.write("\n")
            task = self._tasks[name]
            if path := task.get("request"):
                buf.write("    Request: ")
                buf.write(str(path))
                buf.write("\n")
            react = self._react_as_commands(task.get("react"))
            if react:
                buf.write("    React commands:\n")
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
