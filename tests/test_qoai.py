import pytest

import qoai

from os import listdir
from pathlib import Path


CASES_DIR = Path(__file__).parent / "cases"

TEXT = "Hello. World."
TEXT_LINED = "Hello.\nWorld.\n"


def mock_query_openai(req):
    ret = dict(
        created=1674259148,
        choices=[dict(text=TEXT)],
    )
    return ret


qoai.live_query_openai = mock_query_openai


def test_main(tmp_path):
    srcpath = str(tmp_path / "source.txt")
    open(srcpath, "w").write(TEXT)
    qoai.main(["--set", "set/grammar.xml", srcpath, "--log", str(tmp_path)])
    got = open(srcpath + ".R1").read()
    assert got == TEXT_LINED


def test_trivial_diffs():
    assert qoai.diffadapt("Whatever", [""]) == [""]
    assert qoai.diffadapt("Hello", ["World"]) == ["World"]


@pytest.mark.parametrize("case", listdir(CASES_DIR / "diff"))
def test_diffadapt(case):
    txt = {}
    for key in ["orig", "revised", "expected"]:
        path = CASES_DIR / "diff" / case / (key + ".txt")
        txt[key] = open(path).read()

    got = qoai.diffadapt(txt["orig"], [txt["revised"]])[0]
    assert got == txt["expected"]
