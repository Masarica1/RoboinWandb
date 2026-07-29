from pathlib import Path
import subprocess
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict
import wandb

class EnvSettings(BaseSettings):
    wandb_key: str
    cyclo_lab_path: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8"
    )


settings = EnvSettings() # type: ignore
wandb.login(key=settings.wandb_key)

cyclo_path = Path(settings.cyclo_lab_path)
assert cyclo_path.exists(), f'지정한 형태의 cyclo lab path가 없습니다.'

for tb_path in cyclo_path.iterdir():
    if not tb_path.is_dir():
        continue

    subprocess.run(
        [sys.executable, '-m', 'wandb', 'sync', '--legacy', '--project', tb_path.name], check=True
    )




