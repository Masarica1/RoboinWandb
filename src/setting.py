from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath

class EnvSettings(BaseSettings):
    wandb_key: str
    cyclo_lab_path: DirectoryPath

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8"
    )