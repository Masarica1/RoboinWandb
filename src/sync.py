from pathlib import Path
from tensorboard.backend.event_processing import event_accumulator

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

            # set accumulator
            accumulator = event_accumulator.EventAccumulator(
                path=str(tb_path),
                size_guidance={'scalars': 0}
            )
            accumulator.Reload()

            # init wandb
            wandb.init(
                project=project_path.name,
                name=tb_path.name
            )

            step_to_logs = {}
            tags = accumulator.Tags()['scalars']
            for tag in tags:
                events = accumulator.Scalars(tag)
                for event in events:
                    step = event.step
                    val = event.value
                    
                    if step not in step_to_logs:
                        step_to_logs[step] = {}
                    
                    step_to_logs[step][tag] = val

            for step in sorted(step_to_logs.keys()):
                log_dict = step_to_logs[step]
                
                # wandb step 축을 텐서보드의 step과 정확히 맞춰서 로깅
                wandb.log(log_dict, step=step)
            wandb.finish()
print("WandB 마이그레이션 완료!")



