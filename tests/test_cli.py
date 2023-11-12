import pytest

import copyaid.cli


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

copyaid.core.ApiProxy.ApiClass = MockApi

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
