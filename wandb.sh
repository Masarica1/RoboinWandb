#!/bin/bash

# 오류 발생 시 즉시 실행 중단
set -e

# 현재 스크립트가 있는 디렉터리로 이동 (어느 위치에서 실행하든 정상 동작하도록 보장)
cd "$(dirname "$0")"

echo "가상환경(.venv) 활성화 중..."
source ./.venv/bin/activate

echo "src/main.py 실행 중..."
python src/main.py

echo "가상환경 비활성화 중..."
deactivate

echo "완료되었습니다."