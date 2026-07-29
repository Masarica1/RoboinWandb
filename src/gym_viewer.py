from pathlib import Path
from typing import Literal
import subprocess
import sys
import ast
import re


from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

INIT_FILE_PATH = '/home/robotis-ai/roboin_ws/cyclo_lab_private/source/cyclo_lab/cyclo_lab/simulation_tasks/manager_based/mimic/config/k1_rev1/__init__.py'
CHECKPOINT_PATH = '/home/robotis-ai/roboin_ws/cyclo_lab_private/logs/rsl_rl'

def get_task_ids() -> list[str]:
    file_str = Path(INIT_FILE_PATH).read_text()
    ast_tree = ast.parse(file_str, filename=INIT_FILE_PATH)

    result_list: list[str] = []
    for node in ast.walk(ast_tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "gym"
            and node.func.attr == "register"
        ):
            for keyword in node.keywords:
                if (keyword.arg == 'id') and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    result_list.append(keyword.value.value)

    return result_list

def get_checkpoint_path(run_id: str) -> Path:
    DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}")
    MODEL_PATTERN = re.compile(r"model_(\d+)\.pt")

    checkpoint_dir = Path(CHECKPOINT_PATH) / run_id.lower()

    if not checkpoint_dir.is_dir():
        raise FileNotFoundError(f"체크포인트 디렉토리가 없습니다: {checkpoint_dir}")

    latest_data_dir = max(
        (
            path
            for path in checkpoint_dir.iterdir()
            if path.is_dir() and DATE_PATTERN.fullmatch(path.name)
        ),
        key=lambda path: path.name,
        default=None,
    )

    if latest_data_dir is None:
        raise FileNotFoundError(f"실행 디렉토리가 없습니다: {checkpoint_dir}")

    latest_model = max(
        (
            (int(match.group(1)), file)
            for file in latest_data_dir.iterdir()
            if file.is_file()
            and (match := MODEL_PATTERN.fullmatch(file.name))
        ),
        key=lambda item: item[0],
        default=None,
    )

    if latest_model is None:
        raise FileNotFoundError(f"모델 파일이 없습니다: {latest_data_dir}")

    return latest_model[1]



@app.get('/tasks')
def get_task_list() -> list[str]:
    return sorted(get_task_ids())


@app.post('/play/{id}')
def play_task(id: str, num_envs: int = 16) -> bool:
    # 문자열 전처리
    id = id.strip()
    if id[0] == '"': id = id[1:]
    if id[-1] == ',': id = id[:-1]
    if id[-1] == '"': id = id[:-1]

    if id not in get_task_ids():
        raise HTTPException(status_code=404, detail='id is not registered on gym registry')

    subprocess.Popen(
    [
        sys.executable,
        'scripts/reinforcement_learning/rsl_rl/play.py',
        '--task', id,
        f'--num_envs={num_envs}'
    ]
    )
    return True

@app.post('/record/{id}')
def record_task(id: str, num_envs: int = 16, video_length: int = 500,checkpoint: str|None = None):
    # 문자열 전처리
    id = id.strip()
    if id[0] == '"': id = id[1:]
    if id[-1] == ',': id = id[:-1]
    if id[-1] == '"': id = id[:-1]

    if id not in get_task_ids():
        raise HTTPException(status_code=404, detail='해당 id가 gym registry에 등록되지 않았습니다.')

    # 체크포인트 전처리
    checkpoint_path: Path
    if isinstance(checkpoint, str):
        checkpoint_path = Path(checkpoint)
    else:
        checkpoint_path = get_checkpoint_path(id)

    subprocess.Popen(
    [
        sys.executable,
        'scripts/reinforcement_learning/rsl_rl/play.py',
        '--video', f'--video_length={video_length}',
        '--headless',
        '--task', id,
        f'--num_envs={num_envs}',
        f'--checkpoint {checkpoint_path}'
    ]
    )

    


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8008)

    

