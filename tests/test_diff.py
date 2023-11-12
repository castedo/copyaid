import pytest

import copyaid.diff
from copyaid.diff import diffadapt

from os import listdir
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"


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
        tokens._do_operation(tag, rev_chunk, orig_chunk)
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
