import pytest

import copyaid.cli
from copyaid.diff import diffadapt

from os import listdir
from pathlib import Path


CASES_DIR = Path(__file__).parent / "cases"


SOURCE_TEXT = "Jupiter big.\nJupiter a planet.\nJupiter gas.\n"
MOCK_COMPLETION = "Jupiter is a big planet made of gas."
EXPECTED_TEXT = "Jupiter is\na big planet\nmade of gas.\n"

class MockApi:
    def __init__(self, api_key_path):
        pass

    def query(self, req):
        ret = dict(
            created=1674259148,
            choices=[dict(message=dict(content=MOCK_COMPLETION))],
        )
        return ret

copyaid.cli.CopyAid.ApiClass = MockApi

def test_main(tmp_path):
    srcpath = tmp_path / "source.txt"
    open(srcpath, "w").write(SOURCE_TEXT)
    retcode = copyaid.cli.main([
        "proof",
        str(srcpath),
        "--dest", str(tmp_path),
        "--config", "tests/mock_config.toml",
    ])
    assert retcode == 0
    got = open(tmp_path / "R1" / srcpath.name).read()
    assert got == EXPECTED_TEXT


def test_trivial_diffs():
    assert diffadapt("Whatever\n", [""]) == ["\n"]
    assert diffadapt("Hello\n", ["World"]) == ["World\n"]


def print_operations(orig_text, rev_text):
    matcher = copyaid.diff.TokenSequenceMatcher(orig_text)
    matcher.set_alternative(rev_text)
    tokens = copyaid.diff.DiffAdaptedRevisionTokens()
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


def read_text_files(subcase_dir):
    ret = dict()
    for path in subcase_dir.iterdir():
        assert path.suffix == ".txt"
        with open(path) as file:
            ret[path.stem] = file.read()
    return ret 


@pytest.mark.parametrize("case", listdir(CASES_DIR / "diff"))
def test_diffadapt(case):
    txt = read_text_files(CASES_DIR / "diff" / case)
    #print_operations(txt["orig"], txt["revised"])
    got = diffadapt(txt["orig"], [txt["revised"]])[0]
    assert got == txt["expected"]


@pytest.mark.parametrize("case", listdir(CASES_DIR / "undo"))
def test_diffadapt_undo(case):
    txt = read_text_files(CASES_DIR / "undo" / case)
    #print_operations(txt["orig"], txt["revised"])
    got = diffadapt(txt["orig"], [txt["revised"]])[0]
    assert got == txt["orig"]
