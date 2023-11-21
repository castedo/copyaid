import tomli
from .core import ApiProxy

# Python Standard Library
import filecmp, io, os, subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional
from warnings import warn


class Config:
    @dataclass
    class Task:
        settings: Any
        react: list[str]
        clean: bool

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

    def get_api_proxy(self, log_path: Path) -> ApiProxy:
        api_key = None
        api_key_path = self._data.get("openai_api_key_file")
        api_key_path = self._resolve_path(api_key_path)
        if api_key_path is not None:
            with open(api_key_path, 'r') as file:
                api_key = file.read().strip()
        return ApiProxy(api_key, log_path, self.log_format)

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
        react = self._react_as_commands(task.get("react"))
        clean = task.get("clean", False)
        return Config.Task(settings, react, clean)

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

class Task:
    MAX_NUM_REVS = 7

    def __init__(self, dest: Path, config: Config, task_name: str):
        tconfig = config.get_task(task_name)
        if tconfig is None:
            raise ValueError(f"Invalid task name {task_name}.")
        self.dest = dest
        self.settings = tconfig.settings
        self.react = tconfig.react
        self.clean = tconfig.clean
        if self.settings is not None:
            num_revs = self.settings.get("n", 1)
            if num_revs > Task.MAX_NUM_REVS:
                self.settings["n"] = Task.MAX_NUM_REVS
                msg = "{} revisions requested, changed to max {}"
                warn(msg.format(num_revs, Task.MAX_NUM_REVS))
        if self.clean and not self.settings:
            self.clean = False
            msg = "Setting clean=true ignored for task {} since there is no request."
            warn(msg.format(task_name))

    def rev_dest_glob(self, src: Path) -> str:
        return str(self.dest) + "/R?/" + src.name

    def _rev_paths(self, src_path: Path) -> list[Path]:
        ret = list()
        pattern = str(self.dest) + "/R{}/" + src_path.name
        for i in range(Task.MAX_NUM_REVS):
            ret.append(Path(pattern.format(i + 1)))
        return ret

    def use_saved_revision(self, src: Path) -> Optional[Path]:
        if not self.clean:
            R1 = self.dest / "R1" / src.name
            R2 = self.dest / "R2" / src.name
            if R1.exists() and not R2.exists():
                if filecmp.cmp(src, R1, shallow=False):
                    return R1
        return None

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
                args = [str(src_path)] + found_revs
                for cmd in self.react:
                    proc = subprocess.run([cmd] + args, shell=True)
                    ret = proc.returncode
                    if ret:
                        break
        return ret
