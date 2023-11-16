import os

import pytest

import useenv

CONFIG = r"""env_file: .testenv
envs:
    e1:
        FOO: e1foo
        BAR: e1bar
    e2:
        FOO:
        BAR: ""
        BAX: e2bax
    extra:
        FOO: extrafoo
        HELLO: World
    newlinevalues:
        FOO: "foo\nfoo"
    escapednewlinevalues:
        FOO: "foo\\nfoo"
"""

ENV = r"""FOO="foo"
BAR="bar"
BAZ="baz"
BAX=
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
            == r"""FOO="e1foo"
BAR="e1bar"
BAZ="baz"
BAX=
"""
        )

    useenv.useenv("e2", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == r"""FOO=
BAR=""
BAZ="baz"
BAX="e2bax"
"""
        )

    with pytest.raises(useenv.UnknownEnv):
        useenv.useenv("unknown", mode=useenv.Mode.MERGE)


def test_merge_extra_keys(files):
    useenv.useenv("extra", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == r"""FOO="extrafoo"
BAR="bar"
BAZ="baz"
BAX=
HELLO="World"
"""
        )


def test_newlines_in_values(files):
    useenv.useenv("newlinevalues", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == r"""FOO="foo\nfoo"
BAR="bar"
BAZ="baz"
BAX=
"""
        )

    useenv.useenv("escapednewlinevalues", mode=useenv.Mode.MERGE)
    with open(".testenv") as f:
        assert (
            f.read()
            == r"""FOO="foo\\nfoo"
BAR="bar"
BAZ="baz"
BAX=
"""
        )


def test_create(files):
    useenv.useenv("e1", mode=useenv.Mode.CREATE)
    with open(".testenv") as f:
        assert (
            f.read()
            == r"""FOO="e1foo"
BAR="e1bar"
"""
        )

    with pytest.raises(useenv.UnknownEnv):
        useenv.useenv("unknown", mode=useenv.Mode.CREATE)
