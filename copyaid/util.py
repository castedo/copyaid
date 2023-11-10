# Python standard libraries
import os, shutil
from importlib import resources
from pathlib import Path

STD_BASE_DIRS = dict(
    TMPDIR="/tmp",
    XDG_CONFIG_HOME="~/.config",
    XDG_STATE_HOME="~/.local/state",
)


def get_std_path(env_var_name: str, subpath: str) -> Path:
    base_dir = os.environ.get(env_var_name)
    if base_dir is None:
        base_dir = STD_BASE_DIRS[env_var_name]
    return Path(base_dir).expanduser() / subpath


def copy_package_file(filename: str, dest: Path) -> None:
    rp = resources.files(__package__).joinpath("data").joinpath(filename)
    with resources.as_file(rp) as filepath:
        os.makedirs(dest.parent, exist_ok=True)
        shutil.copy(filepath, dest)
