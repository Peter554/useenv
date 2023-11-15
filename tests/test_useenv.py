import os

import pytest

import useenv

CONFIG = """\
env_file: .testenv
envs:
    e1:
        FOO: e1foo
        BAR: e1bar
    e2:
        FOO: e2foo
        BAR: e2bar
    extra:
        FOO: extrafoo
        HELLO: World
"""

ENV = """\
FOO=foo
BAR=bar
BAZ=baz
"""


@pytest.fixture()
def files():
    with open(".useenv.yml", "w") as f:
        f.write(CONFIG)
    with open(".testenv", "w") as f:
        f.write(ENV)
    yield
    os.remove(".useenv.yml")
    os.remove(".testenv")


def test_merge(files):
    useenv.useenv("e1", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == """\
FOO=e1foo
BAR=e1bar
BAZ=baz
"""
        )

    useenv.useenv("e2", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == """\
FOO=e2foo
BAR=e2bar
BAZ=baz
"""
        )

    with pytest.raises(useenv.UnknownEnv):
        useenv.useenv("unknown", mode=useenv.Mode.MERGE)


def test_merge_extra_keys(files):
    useenv.useenv("extra", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == """\
FOO=extrafoo
BAR=bar
BAZ=baz
HELLO=World
"""
        )


def test_create(files):
    useenv.useenv("e1", mode=useenv.Mode.CREATE)
    with open(".testenv") as f:
        assert (
            f.read()
            == """\
FOO=e1foo
BAR=e1bar
"""
        )

    with pytest.raises(useenv.UnknownEnv):
        useenv.useenv("unknown", mode=useenv.Mode.CREATE)
