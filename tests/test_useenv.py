import os

import pytest

import useenv

CONFIG = """
env_file: .testenv
envs:
    e1:
        FOO: e1foo
        BAR: e1bar
    e2:
        FOO: e2foo
        BAR: e2bar
    oops:
        HELLO: oops
        WORLD: oopsoops
"""

ENV = """
FOO=foo

BAR=bar

BAZ=baz
"""


@pytest.fixture()
def files():
    with open(".useenv", "w") as f:
        f.write(CONFIG)
    with open(".testenv", "w") as f:
        f.write(ENV)
    yield
    os.remove(".useenv")
    os.remove(".testenv")


def test_useenv(files):
    useenv.useenv("e1")
    with open(".testenv") as f:
        assert (
            f.read()
            == """
FOO=e1foo

BAR=e1bar

BAZ=baz
"""
        )

    useenv.useenv("e2")
    with open(".testenv") as f:
        assert (
            f.read()
            == """
FOO=e2foo

BAR=e2bar

BAZ=baz
"""
        )

    with pytest.raises(useenv.UnknownEnv):
        useenv.useenv("unknown")


def test_key_not_found(files):
    with pytest.raises(useenv.KeyNotFound) as exc_info:
        useenv.useenv("oops")

    assert str(exc_info.value) == "No key found for keys: HELLO, WORLD"
