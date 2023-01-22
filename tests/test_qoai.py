import pytest

import qoai

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
    qoai.main(["set/grammar.xml", srcpath, str(tmp_path)])
    got = open(srcpath + ".R1").read()
    assert got == TEXT_LINED
