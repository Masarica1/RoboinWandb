import argparse
import asyncio
import time

from src.sync import sync, EXECUTOR

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, help='총 실행 시간 (hour)', required=True)
    args = parser.parse_args()

    period: int = int(args.time * 60 * 60)  # seconds
    start_time = time.time()

    print('W&B syncronizing is started.')
    print(f'It lasts for {args.time} hours')

    try:
        while True:
            asyncio.run(sync())

            end_time = time.time()
            if end_time - start_time > period:
                break
            time.sleep(10 * 30)
    finally:
        EXECUTOR.shutdown(wait=True)

if __name__ == '__main__':
    main()

    