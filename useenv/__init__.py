import collections
import enum
import json
import os
import pathlib
import subprocess
from typing import Optional

import typer
import yaml

cli = typer.Typer()


class ConfigNotFound(Exception):
    ...


class UnknownEnv(Exception):
    ...


class FailedToFetchFrom1Pw(Exception):
    ...


class Mode(enum.Enum):
    MERGE = "merge"
    CREATE = "create"


@cli.command()
def useenv(
    env_identifier: str,
    dry: bool = False,
    mode: Optional[Mode] = None,  # noqa:UP007
) -> None:
    config_path, config = _get_config()
    env_file_path = config_path.parent / config["env_file"]

    mode = mode or Mode(config.get("mode", "merge"))
    if mode == Mode.MERGE:
        _merge(config, env_file_path, env_identifier, dry)
    elif mode == Mode.CREATE:
        _create(config, env_file_path, env_identifier, dry)


def _merge(config: dict, env_file_path: str, env_identifier: str, dry: bool) -> None:
    try:
        delta_env = config["envs"][env_identifier]
    except KeyError as e:
        raise UnknownEnv(f"{env_identifier} is not a configured environment") from e

    _substitute_values(delta_env)

    try:
        with open(env_file_path) as f:
            current_env_lines = f.read().splitlines(keepends=False)
    except FileNotFoundError:
        current_env_lines = []

    new_env_lines = []
    for line in current_env_lines:
        if not line or line.startswith("#"):
            new_env_lines.append(line)
            continue
        key, _ = line.split("=", maxsplit=1)
        if key in delta_env:
            new_value = delta_env.pop(key)
            new_env_lines.append(f"{key}={new_value}")
        else:
            new_env_lines.append(line)

    for k, v in delta_env.items():
        new_env_lines.append(f"{k}={v}")

    new_env = "\n".join(new_env_lines) + "\n"

    if dry:
        print(new_env)
    else:
        with open(env_file_path, "w") as f:
            f.write(new_env)


def _create(config: dict, env_file_path: str, env_identifier: str, dry: bool) -> None:
    try:
        env = config["envs"][env_identifier]
    except KeyError as e:
        raise UnknownEnv(f"{env_identifier} is not a configured environment") from e

    _substitute_values(env)

    new_env_lines = [f"{k}={v}" for k, v in env.items()]
    new_env = "\n".join(new_env_lines) + "\n"

    if dry:
        print(new_env)
    else:
        with open(env_file_path, "w") as f:
            f.write(new_env)


def _get_config() -> tuple[pathlib.Path, dict]:
    config_directory = pathlib.Path(os.getcwd())
    found = False
    while True:
        for config_path in [
            config_directory / ".useenv",
            config_directory / ".useenv.yml",
            config_directory / ".useenv.yaml",
        ]:
            if config_path.is_file():
                found = True
                break
        if found:
            break
        else:
            if config_directory == pathlib.Path("/"):
                raise ConfigNotFound
            config_directory = config_directory.parent

    with open(config_path) as f:
        config = yaml.safe_load(f)

    return config_path, config


def _substitute_values(env: dict) -> None:
    for k, v in env.items():
        if v is None:
            env[k] = ""
        else:
            env[k] = str(v)

    _substitute_1pw_values(env)


def _substitute_1pw_values(env: dict) -> None:
    items_to_fetch: dict[str, list[str]] = collections.defaultdict(list)
    fetched_items: dict[str, dict[str, str]] = collections.defaultdict(dict)

    for k, v in env.items():
        if v.startswith("1pw::"):
            _, item_id, field = v.split("::")
            items_to_fetch[item_id].append(field)

    for item_id, fields_to_fetch in items_to_fetch.items():
        fetched_items[item_id] = _get_values_from_1pw(item_id, fields_to_fetch)

    for k, v in env.items():
        if v.startswith("1pw::"):
            _, item_id, field = v.split("::")
            env[k] = fetched_items[item_id][field]


def _get_values_from_1pw(item_id: str, fields: list[str]) -> dict:
    if not fields:
        return {}
    result = subprocess.run(
        [
            "op",
            "item",
            "get",
            item_id,
            "--fields",
            ",".join(f"label={f}" for f in fields),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    try:
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        raise FailedToFetchFrom1Pw(result.stderr.strip()) from e
    result_json = json.loads(result.stdout.strip())
    if len(fields) == 1:
        return {result_json["label"]: str(result_json["value"])}
    else:
        return {field["label"]: str(field["value"]) for field in result_json}
