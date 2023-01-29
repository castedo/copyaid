import pytest

import qoai

from os import listdir
from pathlib import Path


CASES_DIR = Path(__file__).parent / "cases"


SOURCE_TEXT = "Jupiter big.\nJupiter a planet.\nJupiter gas.\n"
MOCK_COMPLETION = "Jupiter is a big planet made of gas."
EXPECTED_TEXT = "Jupiter is\n a big planet\n made of gas.\n"

def mock_query_openai(req):
    ret = dict(
        created=1674259148,
        choices=[dict(text=MOCK_COMPLETION)],
    )
    return ret

qoai.live_query_openai = mock_query_openai


def test_main(tmp_path):
    srcpath = str(tmp_path / "source.txt")
    open(srcpath, "w").write(SOURCE_TEXT)
    qoai.main(["--set", "set/grammar.xml", srcpath, "--log", str(tmp_path)])
    got = open(srcpath + ".R1").read()
    assert got == EXPECTED_TEXT


def test_trivial_diffs():
    assert qoai.diffadapt("Whatever\n", [""]) == ["\n"]
    assert qoai.diffadapt("Hello\n", ["World"]) == ["World\n"]


def print_operations(orig_text, rev_text):
    matcher = qoai.TokenSequenceMatcher(orig_text)
    matcher.set_alternative(rev_text)
    tokens = qoai.DiffAdaptedRevisionTokens()
    for tag, rev_chunk, orig_chunk in matcher.operations():
        if tag == 'equal':
            print("==", repr(rev_chunk))
        elif tag == 'delete':
            print("+>", repr(rev_chunk))
        elif tag == 'insert':
            print(repr(orig_chunk), "x>")
        elif tag == 'replace':
            print(repr(orig_chunk), ">>", repr(rev_chunk))
        if tag == "equal":
            tokens.append_unrevised(rev_chunk)
        else:
            tokens.append_revised(rev_chunk, orig_chunk)
        print("DEBT LEFT:", tokens.line_debt)


@pytest.mark.parametrize("case", listdir(CASES_DIR / "diff"))
def test_diffadapt(case):
    txt = {}
    for key in ["orig", "revised", "expected"]:
        path = CASES_DIR / "diff" / case / (key + ".txt")
        txt[key] = open(path).read()

    #print_operations(txt["orig"], txt["revised"])
    got = qoai.diffadapt(txt["orig"], [txt["revised"]])[0]
    assert got == txt["expected"]
