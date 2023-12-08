import pytest

import copyaid.diff
from copyaid.diff import diffadapt

from os import listdir
from pathlib import Path

CASES_DIR = Path(__file__).parent / "cases"


def test_trivial_diffs():
    assert diffadapt("Whatever\n", [""]) == ["\n"]
    assert diffadapt("Hello\n", ["World"]) == ["World\n"]


def print_operation(rev, orig):
    orig_repr = repr("".join(orig))
    rev_repr = repr("".join(rev))
    if rev == orig:
        print("EQU:", rev_repr)
    elif not rev:
        print("DEL:", orig_repr)
    elif not orig:
        print("INS:", rev_repr)
    else:
        print("ORI:", orig_repr)
        print("REV:", rev_repr)


class OperationsPrinter(copyaid.diff.DiffAdaptor):
    
    def _do_operation(self, tag, rev, orig):
        assert (tag == 'equal') == (rev == orig)
        #print_operation(rev, orig)
        ret = super()._do_operation(tag, rev, orig)
        tokens = repr("".join(ret))
        last_token = repr(self.last_token)
        print("DEBT/OUT/LAST: {}/{}/{}".format(self.line_debt, tokens, last_token))

    def _undo_delete(self, orig):
        print_operation([], orig)
        return super()._undo_delete(orig)

    def _adapt_unrevised(self, rev):
        print_operation(rev, rev)
        return super()._adapt_unrevised(rev)

    def _adapt_revised(self, rev, orig):
        print_operation(rev, orig)
        return super()._adapt_revised(rev, orig)


def print_operations(orig_text, rev_text):
    matcher = copyaid.diff.TokenSequenceMatcher(orig_text)
    matcher.set_alternative(rev_text)
    tokens = OperationsPrinter()
    for tag, rev_chunk, orig_chunk in matcher.operations():
        tokens._do_operation(tag, rev_chunk, orig_chunk)


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
