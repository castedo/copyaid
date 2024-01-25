import pytest

import copyaid.cli

import os
from types import SimpleNamespace

SOURCE_TEXT = "Jupiter big.\nJupiter a planet.\nJupiter gas.\n"
MOCK_COMPLETION = "Jupiter is a big planet made of gas."
EXPECTED_TEXT = "Jupiter is\na big planet made of\ngas.\n"

class MockApi:
    def __init__(self, api_key):
        pass

    def query(self, req):
        return SimpleNamespace(
            created=1674259148,
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=MOCK_COMPLETION
                    )
                )
            ]
        )

copyaid.core.ApiProxy.ApiClass = MockApi


def get_revision(src_path, src_text, task="proof"):
    open(src_path, "w").write(src_text)
    retcode = copyaid.cli.main([
        task,
        str(src_path),
        "--dest", str(src_path.parent),
        "--config", "tests/mock_config.toml",
    ])
    assert retcode == 0
    return open(src_path.parent / "R1" / src_path.name).read()


def test_main(tmp_path):
    got = get_revision(tmp_path / "source.txt", SOURCE_TEXT)
    assert got == EXPECTED_TEXT


def test_copybreak_md(tmp_path):
    copybreak = "<!-- copybreak -->\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.md", src_text)
    assert got == EXPECTED_TEXT + copybreak + EXPECTED_TEXT

def test_copybreak_off_md(tmp_path):
    copybreak = "<!-- copybreak off -->\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.md", src_text)
    assert got == EXPECTED_TEXT + copybreak + SOURCE_TEXT

def test_copybreak_tex(tmp_path):
    copybreak = "%% copybreak\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.tex", src_text)
    assert got == EXPECTED_TEXT + copybreak + EXPECTED_TEXT

def test_copybreak_off_tex(tmp_path):
    copybreak = "%% copybreak off\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.tex", src_text)
    assert got == EXPECTED_TEXT + copybreak + SOURCE_TEXT

def test_copybreak_foobar(tmp_path):
    copybreak = "¡¿ copybreak ?!\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.foobar", src_text, "fooit")
    assert got == EXPECTED_TEXT + copybreak + EXPECTED_TEXT

def test_copybreak_off_foobar(tmp_path):
    copybreak = "¡¿ copybreak off ?!\n"
    src_text = SOURCE_TEXT + copybreak + SOURCE_TEXT
    got = get_revision(tmp_path / "source.foobar", src_text, "fooit")
    assert got == EXPECTED_TEXT + copybreak + SOURCE_TEXT
