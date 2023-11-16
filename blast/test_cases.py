#!/usr/bin/python3

import tomli

# Python Standard Library
import filecmp, os, shutil, subprocess, tempfile
from pathlib import Path
from typing import Optional

CASES_DIR = Path(__file__).parent / "cases"
MAX_REQUESTS = 5

COPYAID_TOML_TEMPLATE = '''
openai_api_key_file = "~/.config/copyaid/openai_api_key.txt"
log_format = "jsoml"
tasks.it.request = "{}"
'''


def files_match(a: Path, b: Path) -> bool:
    return filecmp.cmp(a, b, shallow=False)


def write_config(settings_path: Path, tmp_dir: Path) -> None:
    with open(settings_path, "rb") as file:
        settings = tomli.load(file)
    assert settings["openai"]["n"] == 1
    assert settings["openai"]["temperature"] == 0
    with open(tmp_dir / "copyaid.toml", "w") as file:
        file.write(COPYAID_TOML_TEMPLATE.format(settings_path))


class Blaster:
    def __init__(self, case: Path, tmp_dir: Path):
        self.tmp_dir = Path(tmp_dir)
        assert self.tmp_dir.is_dir()
        write_config(case / "settings.toml", tmp_dir)
        self.codeword = None
        try:
            with open(case / "codeword", 'r') as file:
                self.codeword = file.read().strip()
        except:
            pass
        if self.codeword:
            self.react = 'diffadapt -c {} "$0" "$@"'.format(self.codeword)
        else:
            self.react = 'diffadapt "$0" "$@"'

    def diffadapt(self, src: Path) -> Path:
        ret = self.tmp_dir / "R1" / src.name
        codeword_found = False
        if self.codeword:
            with open(ret, 'r') as file:
                codeword_found = (self.codeword == file.read().strip())
        # emulate how diffadapt called
        cmdline = [self.react, str(src), str(ret)]
        print(cmdline)
        subprocess.run(cmdline, shell=True, check=True)
        if self.codeword and not codeword_found:
            if files_match(src, ret):
                print("WARNING! Codeword not returned when no changes.", ret)
        return ret

    def copyaidit(self, src: Path) -> Path:
        tmp = str(self.tmp_dir)
        cmdline = ["copyaid", "it", "-c", tmp, "-d", tmp, str(src)]
        print(cmdline)
        subprocess.run(cmdline, check=True)
        return self.diffadapt(src)

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


def blast(case: Path, tmp_dir: Path) -> None:
    blaster = Blaster(case, tmp_dir)
    noloop = Path(case / "noloop").exists()
    for group in os.listdir(case / "input"):
        print(group)
        for filename in os.listdir(case / "input" / group):
            src = case / "input" / group / filename
            outs = list()
            for i in range(0, MAX_REQUESTS):
                outs.append(case / "output" / group / str(i + 1) / filename)
            if noloop:
                blaster.get_first_output(src, outs[0])
            else:
                final = case / "final" / group / filename
                blaster.get_final(src, final, outs)


def main(cmd_line_args=None):
    with tempfile.TemporaryDirectory() as tmp_dir:
        for case in CASES_DIR.iterdir():
            print(case.name)
            blast(case, Path(tmp_dir))


if __name__ == "__main__":
    exit(main())
