#!/bin/bash

# 총 실행 시간(분) 변수 초기화
TOTAL_TIME=0

# -t 옵션 인자 파싱
while getopts "t:" opt; do
  case $opt in
    t) TOTAL_TIME=$OPTARG ;;
    \?) echo "사용법: $0 -t <실행할_시간(분)>"; exit 1 ;;
  esac
done

# 입력값 검증 (숫자인지, 0보다 큰지 확인)
if ! [[ "$TOTAL_TIME" =~ ^[0-9]+$ ]] || [ "$TOTAL_TIME" -le 0 ]; then
    echo "오류: -t 옵션에 양의 정수(분 단위)를 입력해주세요."
    echo "예시: $0 -t 60  (60분 동안 실행)"
    exit 1
fi

# 종료 시간 계산
START_TIME=$(date +%s)
END_TIME=$((START_TIME + TOTAL_TIME * 60))

echo "=== W&B 자동 동기화 시작 (총 ${TOTAL_TIME}분 동안 10분 간격 실행) ==="
echo "종료 예정 시간: $(date -d @$END_TIME '+%Y-%m-%d %H:%M:%S')"

# 현재 시간이 종료 시간보다 작은 동안 루프 실행
while [ $(date +%s) -lt $END_TIME ]
do
    echo "------------------------------------------------"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] W&B sync 작업 시작"
    
    echo "가상환경(.venv) 활성화 중..."
    source ./.venv/bin/activate
    
    echo "W&B sync 실행 중..."
    python src/sync.py
    
    echo "가상환경 비활성화 중..."
    deactivate
    
    echo "작업 완료."
    
    # 남은 시간 확인
    CURRENT_TIME=$(date +%s)
    REMAINING_TIME=$((END_TIME - CURRENT_TIME))
    
    # 남은 시간이 10분(600초) 미만이면 추가 대기 없이 루프를 종료
    if [ $REMAINING_TIME -lt 600 ]; then
        echo "남은 시간이 10분 미만이므로 대기하지 않고 스케줄러를 종료합니다."
        break
    fi
    
    echo "다음 실행을 위해 10분(600초) 대기 중..."
    sleep 600
done

echo "================================================"
echo "=== 설정된 시간(${TOTAL_TIME}분)이 경과되어 스크립트를 종료합니다. ==="