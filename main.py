import argparse
import time

from src.sync import sync

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', type=int, help='총 실행 시간 (hour)')
    args = parser.parse_args()

    period: int = int(args.time * 60 * 60)  # seconds
    start_time = time.time()

    print('W&B syncronizing is started.')
    print(f'It lasts for {args.time} hours')

    while True:
        sync()

        end_time = time.time()
        if end_time - start_time > period:
            break
        time.sleep(10 * 60)

        

    