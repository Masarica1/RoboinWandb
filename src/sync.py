from tensorboard.backend.event_processing import event_accumulator
import wandb
from src.setting import EnvSettings


LOG_HEAD = '\033[1mRoboinW&B\033[0m'

def sync():
    settings = EnvSettings() # type: ignore
    wandb.login(key=settings.wandb_key)
    
    # WandB API 초기화
    api = wandb.Api()

    for project_path in settings.cyclo_lab_path.iterdir():
        if not project_path.is_dir():
            continue

        project_name = project_path.name

        for tb_path in project_path.iterdir():
            if not tb_path.is_dir():
                continue
            
            run_name = tb_path.name

            # set accumulator
            accumulator = event_accumulator.EventAccumulator(
                path=str(tb_path),
                size_guidance={'scalars': 0}
            )
            accumulator.Reload()

            step_to_logs = {}
            tags = accumulator.Tags()['scalars']
            for tag in tags:
                events: list[event_accumulator.ScalarEvent] = accumulator.Scalars(tag)
                for event in events:
                    step = event.step
                    val = event.value
                    
                    if step not in step_to_logs:
                        step_to_logs[step] = {}
                    
                    step_to_logs[step][tag] = val
            
            # 로컬 텐서보드 로그가 아예 없는 경우 스킵
            if not step_to_logs:
                continue
                
            # 로컬 로그의 최대 스텝 수 계산
            local_max_step = max(step_to_logs.keys())

            # API를 통해 WandB에 이미 존재하는 동일한 이름의 Run 가져오기
            existing_run = None
            try:
                runs = api.runs(path=project_name, filters={"display_name": run_name})
                if len(runs) > 0:
                    existing_run = runs[0]
            except Exception:
                # 프로젝트가 아직 생성되지 않은 경우 등
                pass

            # 기존 Run이 존재할 경우 스텝 수 비교
            if existing_run:
                # WandB에 저장된 마지막 스텝 번호 가져오기 (없으면 -1)
                remote_max_step = existing_run.summary.get('_step', -1)
                
                if remote_max_step == local_max_step:
                    print(f"{LOG_HEAD}: [{project_name} - {run_name}] this run is not changed & it will not be uploaded")
                    continue
                else:
                    print(f"{LOG_HEAD}: [{project_name} - {run_name}] this run is edited and will be syncronize...")
                    existing_run.delete() # 기존 Run 삭제

            # init wandb
            wandb.init(
                project=project_name,
                name=run_name,
                reinit=True # 반복문 내에서 여러 번 초기화하므로 reinit=True 설정
            )

            for step in sorted(step_to_logs.keys()):
                log_dict = step_to_logs[step]
                
                # wandb step 축을 텐서보드의 step과 정확히 맞춰서 로깅
                wandb.log(log_dict, step=step)
            wandb.finish()
            
    print(f'{LOG_HEAD}: Syncronizer iteration finished')


if __name__ == '__name__':
    sync()
    print(f'{LOG_HEAD}: Syncronizer finished')