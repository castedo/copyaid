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


def print_operations(orig_text, rev_text):
    matcher = qoai.TokenSequenceMatcher(orig_text)
    matcher.set_alternative(rev_text)
    for tag, rev_chunk, orig_chunk in matcher.operations():
        if tag == 'equal':
            print("==", repr(rev_chunk))
        elif tag == 'delete':
            print("+>", repr(rev_chunk))
        elif tag == 'insert':
            print(repr(orig_chunk), "x>")
        elif tag == 'replace':
            print(repr(orig_chunk), ">>", repr(rev_chunk))


@pytest.mark.parametrize("case", listdir(CASES_DIR / "diff"))
def test_diffadapt(case):
    txt = {}
    for key in ["orig", "revised", "expected"]:
        path = CASES_DIR / "diff" / case / (key + ".txt")
        txt[key] = open(path).read()

    #print_operations(txt["orig"], txt["revised"])
    got = qoai.diffadapt(txt["orig"], [txt["revised"]])[0]
    assert got == txt["expected"]
