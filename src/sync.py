from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import asyncio

from tensorboard.backend.event_processing import event_accumulator
from wandb.apis.public import Run, Runs
import wandb

from src.setting import EnvSettings

LOG_HEAD = '\033[1mRoboinW&B\033[0m'
DEBUG_HEAD = '\033[1;33mRoboinW&B-DEBUG\033[0m'
EXECUTOR = ThreadPoolExecutor(4)

@dataclass
class TensorboardData:
    project_path: Path
    tensorboard_path: Path
    tensorboard_data: dict[int, dict[str, float]]


async def get_wandb_run(api: wandb.Api, path: str, run_name: str) -> tuple[int, Run|None]:
    settings = EnvSettings.get()

    def get_run_inside() -> tuple[int, Run|None]:
        runs = api.runs(path=path, filters={"display_name": run_name})

        if not isinstance(runs, Runs):
            raise ValueError("wandb api is something went wrong")

        if len(runs) > 0:
            run = runs[0]
            max_steps: int|None = run.summary.get('_step', -1)

            if not isinstance(max_steps, int):
                raise ValueError("can't get max_step of run")
            return max_steps, run
        else:
            return 0, None

    loop = asyncio.get_running_loop()
    try:
        result = loop.run_in_executor(EXECUTOR, get_run_inside)

        settings.debug_log(f'{DEBUG_HEAD} : {path} - {run_name} W&B 읽기가 시작되었습니다.')
        result.add_done_callback(
            lambda f : settings.debug_log(f'{DEBUG_HEAD} : {path} - {run_name} W&B 읽기가 완료되었습니다.')
            )

        return await result
    except Exception as e:
        print(f'{LOG_HEAD} : error {e}가 발생하였습니다.')
        print(f'{LOG_HEAD} : {path} - {run_name} 항목을 읽기에 실패했습니다.')
        return -1, None



async def sync() -> None:
    settings = EnvSettings.get()
    wandb.login(key=settings.wandb_key)

    api = wandb.Api()

    tensorboard_list: list[TensorboardData] = []

    # 유효한 Tensorboard Data 찾기
    for project_path in settings.cyclo_lab_path.iterdir():
        if not project_path.is_dir():
            continue

        for tb_path in project_path.iterdir():
            if not tb_path.is_dir():
                continue

            # Tf 파일 읽기
            accumulator = event_accumulator.EventAccumulator(
                path=str(tb_path),
                size_guidance={"scalars": 0}
            )
            accumulator.Reload()    

            step_to_logs: dict[int, dict[str, float]] = {}
            tags: list[str] = accumulator.Tags().get("scalars", [])
            for tag in tags:
                events: list[event_accumulator.ScalarEvent] = (accumulator.Scalars(tag))

                for event in events:
                    step = event.step
                    value = event.value

                    if step not in step_to_logs:
                        step_to_logs[step] = {}

                    step_to_logs[step][tag] = value

            # TF 파일이 유효할 경우 추가
            if step_to_logs:
                tensorboard_list.append(TensorboardData(project_path, tb_path, step_to_logs))
    settings.debug_log(f'{DEBUG_HEAD} : 총 {len(tensorboard_list)}개의 TB 데이터가 확인되었습니다.')


    wandb_list = await asyncio.gather(
        *[
            get_wandb_run(api, data.project_path.name, data.tensorboard_path.name)
            for data in tensorboard_list
        ]
    )

    for tb_data, (wandb_step, run) in zip(tensorboard_list, wandb_list):
        tb_step = max(tb_data.tensorboard_data.keys())

        if wandb_step == -1:
            continue

        if tb_step == wandb_step:
            print(
                f'{LOG_HEAD} : [{tb_data.project_path.name} - {tb_data.tensorboard_path.name}]'
                f"학습이 최신버전으로 확인되었습니다. 업데이트를 진행하지 않습니다."
            )
            continue

        print(
            f'{LOG_HEAD} : [{tb_data.project_path.name} - {tb_data.tensorboard_path.name}]'
            f"학습이 업데이트 되었습니다. 새로 업로드를 진행합니다."
        )

        if run is not None:
            run.delete()

        wandb.init(
            project=tb_data.project_path.name,
            name=tb_data.tensorboard_path.name,
            reinit=True
        )

        for step in sorted(tb_data.tensorboard_data.keys()):
            log_dict = tb_data.tensorboard_data[step]
                
                # wandb step 축을 텐서보드의 step과 정확히 맞춰서 로깅
            wandb.log(log_dict, step=step)
        wandb.finish()

    print(f"{LOG_HEAD} 업로드가 완료되었습니다. 5분을 대기합니다.")


if __name__ == "__main__":
    asyncio.run(sync())
    print(f"{LOG_HEAD}: RoboinW&B가 종료되었습니다.")