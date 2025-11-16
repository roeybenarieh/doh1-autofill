import json
from pathlib import Path
from typing import Annotated, Literal

from platformdirs import PlatformDirs
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserConfiguration(BaseModel):
    id_number: Annotated[str, Field(pattern=r"^\d{9}$")]
    microsoft_mail: EmailStr
    microsoft_password: str
    browser_installed: Literal[
        "chrome", "firefox"
    ]  # pretty sure safari doesnt have --headless option(which I need)


class Configuration(UserConfiguration):
    cookies_file_path: Path


def get_config() -> Configuration:
    directories = PlatformDirs(
        appname="doh1-autofill", appauthor="roeyba", ensure_exists=True
    )
    config_file_path = directories.user_config_path / "config.json"
    cookies_file_path = directories.user_data_path / "cookies.pkl"

    with open(config_file_path, "r") as config_file:
        config = json.load(config_file)

    config = Configuration(**config, cookies_file_path=cookies_file_path)
    return config
