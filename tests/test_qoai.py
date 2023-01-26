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
    qoai.main(["--set", "set/grammar.xml", srcpath, "--log", str(tmp_path)])
    got = open(srcpath + ".R1").read()
    assert got == TEXT_LINED


def test_simple_diffs():
    assert qoai.diffadapt("Whatever", [""]) == [""]
    assert qoai.diffadapt("Hello", ["World"]) == ["World"]


def test_jupiter_diff():

    orig = """Jupiter is the largest planet
 in the Solar System.
Jupiter is the fifth planet
 from the Sun.
Jupiter is classified as a gas giant.
This is because
 Jupiter is very big
 and made up of gas.
"""

    revised = """Jupiter is the largest planet in the Solar System and the fifth planet from the Sun.
It is classified as a gas giant due to its immense size and composition of gas."""

    expected = """Jupiter is the largest planet
 in the Solar System
 and the fifth planet
 from the Sun.
It is classified as a gas giant
 due to its immense size and composition of gas.
"""

    got = qoai.diffadapt(orig, [revised])[0]
    assert got == expected

def test_diff_with_commas():

    orig = """XML.
Many JATS XML.
Many appear on both publishers and PubMed.
PubMed is a website.
"""

    revised = "XML, which format that appear on publishers as well as PubMed, a website."

    expected = """XML,
 which format that appear on publishers as well as PubMed,
 a website.
"""
    got = qoai.diffadapt(orig, [revised])[0]
    assert got == expected
