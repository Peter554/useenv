import os
import pathlib
import subprocess

import typer
import yaml

cli = typer.Typer()


class ConfigNotFound(Exception):
    ...


class UnknownEnv(Exception):
    ...


class KeyNotFound(Exception):
    ...

class FailedToFetchFrom1Pw(Exception):
    ...


@cli.command()
def useenv(env_identifier: str, dry: bool = False) -> None:
    config_path, config = _get_config()

    env_file_path = config_path.parent / config["env_file"]
    try:
        delta_env = config["envs"][env_identifier]
    except KeyError as e:
        raise UnknownEnv(f"{env_identifier} is not a configured environment") from e

    with open(env_file_path) as f:
        current_env_lines = f.read().splitlines(keepends=False)

    new_env_lines = []
    for line in current_env_lines:
        if not line or line.startswith("#"):
            new_env_lines.append(line)
            continue
        key, _ = line.split("=", maxsplit=1)
        if key in delta_env:
            new_value = _get_value(delta_env.pop(key))
            new_env_lines.append(f"{key}={new_value}")
        else:
            new_env_lines.append(line)

    if delta_env:
        raise KeyNotFound(f"No key found for keys: {', '.join(delta_env.keys())}")

    new_env = "\n".join(new_env_lines) + "\n"

    if dry:
        print(new_env)
    else:
        with open(env_file_path, "w") as f:
            f.write(new_env)


def _get_config() -> tuple[pathlib.Path, dict]:
    config_path = pathlib.Path(os.getcwd()) / ".useenv"
    while not config_path.is_file():
        config_path = config_path.parent.parent / ".useenv"
        if config_path.parent == pathlib.Path("/"):
            raise ConfigNotFound

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config_path, config


def _get_value(value: str) -> str:
    if value.startswith("1pw::"):
        return _get_value_from_1pw(value)
    else:
        return value


def _get_value_from_1pw(value: str) -> str:
    _, item_id, field = value.split("::")
    result = subprocess.run(
        ["op", "item", "get", item_id, "--field", field], capture_output=True, text=True
    )
    try:
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        raise FailedToFetchFrom1Pw(result.stderr.strip()) from e
    return result.stdout.strip()
