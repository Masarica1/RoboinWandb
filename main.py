import argparse
import asyncio
import time

from src.setting import LOG_HEAD
from src.sync import sync, EXECUTOR

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, help='총 실행 시간 (hour)', required=True)
    args = parser.parse_args()

    period: int = int(args.time * 60 * 60)  # seconds
    start_time = time.time()

    print(f'{LOG_HEAD}: W&B 동기화작업이 시작되었습니다.')
    print(f'{LOG_HEAD}: {args.time} 동안 반복됩니다.')

    try:
        while True:
            asyncio.run(sync())

            end_time = time.time()
            if end_time - start_time > period:
                break
            time.sleep(10 * 30)
    finally:
        EXECUTOR.shutdown(wait=True)
        print(f"{LOG_HEAD}: RoboinW&B가 종료되었습니다.")

if __name__ == '__main__':
    main()

    