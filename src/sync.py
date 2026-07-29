from pathlib import Path
import subprocess
import sys
import os

import wandb

from setting import EnvSettings

if __name__ == '__main__':
    settings = EnvSettings() # type: ignore
    wandb.login(key=settings.wandb_key)

    for project_path in settings.cyclo_lab_path.iterdir():
        if not project_path.is_dir():
            continue

        for tb_path in project_path.iterdir():
            if not tb_path.is_dir():
                continue

            env = os.environ.copy()
            env['WANDB_TENSORBOARD_ROOT'] = str(tb_path)

            subprocess.run(
                [
                    sys.executable, '-m', 'wandb', 'sync', '--legacy',
                    '--project', project_path.name,
                    '--id', tb_path.name,
                    '.'
                ],
                check=True,
                env=env,
                cwd=str(tb_path)
            )




