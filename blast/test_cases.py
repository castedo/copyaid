#!/usr/bin/python3

# Python Standard Library
import filecmp, os, subprocess
import jsoml
from pathlib import Path
from contextlib import chdir

CASES_DIR = Path(__file__).parent / "cases"


def assert_cold_settings(settings_path):
    settings = jsoml.load(Path(settings_path))
    assert settings["openai"]["n"] == 1
    assert settings["openai"]["temperature"] == 0


def copyaidit(src_path):
    cmdline = ["copyaidit.py", "-s", "settings.xml", src_path]
    print(cmdline)
    subprocess.run(cmdline)
    return Path("R1") / src_path.name


def test_case(case_path: Path):
    print(case_path)
    with chdir(case_path):
        assert_cold_settings("settings.xml")
        for group in os.listdir("input"):
            print(group)
            for filename in os.listdir(case_path / "input" / group):
                src_path = Path("input") / group / filename
                final_path = Path("final") / group / filename
                os.makedirs(final_path.parent, exist_ok=True)
                num = 0
                while not os.path.exists(final_path):
                    result = copyaidit(src_path)
                    num += 1
                    assert num < 7
                    if filecmp.cmp(result, src_path, shallow=False):
                        dest_path = final_path
                    else:
                        output_dir = Path("output") / group
                        os.makedirs(output_dir, exist_ok=True)
                        N = 1 + max([0] + [int(s) for s in os.listdir(output_dir)])
                        dest_path = output_dir / str(N) / filename
                        os.makedirs(dest_path.parent, exist_ok=True)
                        src_path = dest_path
                    print(dest_path)
                    os.rename(result, dest_path)


def main(cmd_line_args=None):
    for case in CASES_DIR.iterdir():
        test_case(case)


if __name__ == "__main__":
    exit(main())
