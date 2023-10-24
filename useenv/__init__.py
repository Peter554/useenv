import os
import pathlib

import typer
import yaml

cli = typer.Typer()


class ConfigNotFound(Exception):
    ...



@cli.command()
def useenv(env_identifier: str, dry: bool = False) -> None:
    config_path, config = _get_config()

    env_file_path = config_path.parent / config["env_file"]
    delta_env = config["envs"][env_identifier]

    with open(env_file_path) as f:
        current_env_lines = f.read().splitlines(keepends=False)

    new_env_lines = []
    for line in current_env_lines:
        if not line or line.startswith("#"):
            new_env_lines.append(line)
            continue
        key, value = line.split("=", maxsplit=1)
        if key in delta_env:
            new_env_lines.append(f"{key}={delta_env[key]}")
        else:
            new_env_lines.append(line)
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
