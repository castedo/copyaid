#!/usr/bin/python3

import tomli

# Python Standard Library
import filecmp, os, shutil, subprocess, tempfile
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"
MAX_REQUESTS = 5

COPYAID_TOML_TEMPLATE = '''
openai_api_key_file = "~/.config/copyaid/openai_api_key.txt"
log_format = "jsoml"
tasks.it.request = "{}"
tasks.it.react = ["diffadapt"]
[commands]
diffadapt = 'diffadapt "$0" "$@"'
'''


def files_match(a: Path, b: Path) -> bool:
    return filecmp.cmp(a, b, shallow=False)


def assert_cold_settings(settings_path: Path) -> None:
    with open(settings_path, "rb") as file:
        settings = tomli.load(file)
    assert settings["openai"]["n"] == 1
    assert settings["openai"]["temperature"] == 0


class Blaster:
    def __init__(self, tmp_dir: Path):
        assert tmp_dir.is_dir()
        self.tmp_dir = tmp_dir

    def write_config(self, settings_path: Path) -> None:
        assert_cold_settings(settings_path)
        with open(self.tmp_dir / "copyaid.toml", "w") as file:
            file.write(COPYAID_TOML_TEMPLATE.format(settings_path))

    def copyaidit(self, src: Path) -> Path:
        tmp = str(self.tmp_dir)
        cmdline = ["copyaid", "it", "-c", tmp, "-d", tmp, str(src)]
        print(cmdline)
        subprocess.run(cmdline, check=True)
        return self.tmp_dir / "R1" / src.name

    def get_final(self, src: Path, final: Path, outs: list[Path]) -> None:
        if final.exists():
            print("Skip existing", final)
        files = [src]
        idx = 0
        while not final.exists():
            assert idx < len(outs)
            dest = outs[idx]
            if dest.exists():
                print("Skip existing", dest)
                files.append(dest)
            else:
                result = self.copyaidit(files[-1])
                if any(files_match(result, f) for f in files):
                    dest = final
                else:
                    files.append(dest)
                print(dest)
                os.makedirs(dest.parent, exist_ok=True)
                shutil.copy(result, dest)
            idx += 1

    def get_first_output(self, src: Path, out: Path) -> None:
        if out.exists():
            print("Skip existing", out)
        else:
            result = self.copyaidit(src)
            print(out)
            os.makedirs(out.parent, exist_ok=True)
            shutil.copy(result, out)

    def test(self, case: Path) -> None:
        self.write_config(case / "settings.toml")
        noloop = Path(case / "noloop").exists()
        for group in os.listdir(case / "input"):
            print(group)
            for filename in os.listdir(case / "input" / group):
                src = case / "input" / group / filename
                outs = list()
                for i in range(0, MAX_REQUESTS):
                    outs.append(case / "output" / group / str(i + 1) / filename)
                if noloop:
                    self.get_first_output(src, outs[0])
                else:
                    final = case / "final" / group / filename
                    self.get_final(src, final, outs)


def main(cmd_line_args=None):
    with tempfile.TemporaryDirectory() as tmp_dir:
        blaster = Blaster(Path(tmp_dir))
        for case in CASES_DIR.iterdir():
            print(case.name)
            blaster.test(case)


if __name__ == "__main__":
    exit(main())
