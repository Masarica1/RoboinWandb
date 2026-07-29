from pathlib import Path
import subprocess
import sys

import wandb

from src.setting import EnvSettings

if __name__ == '__main__':
    settings = EnvSettings() # type: ignore
    wandb.login(key=settings.wandb_key)

    for project_path in settings.cyclo_lab_path.iterdir():
        if not project_path.is_dir():
            continue

        for tb_path in project_path.iterdir():
            if not tb_path.is_dir():
                continue

            subprocess.run(
                [
                    sys.executable, '-m', 'wandb', 'sync', '--legacy',
                    '--project', project_path.name,
                    '--id', tb_path.name,
                    str(tb_path)
                ],
                check=True
            )




