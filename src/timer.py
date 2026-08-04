import time

from src.setting import DEBUG_HEAD

class TickTimer:
    def __init__(self) -> None:
        self.last_name: str|None
        self.last_time: float = time.monotonic()

    def start(self, name: str):
        self.last_name = name

    def update(self, name: str):
        print(f'{DEBUG_HEAD}: {self.last_name} 틱 타이머 종료됨 - {time.monotonic() - self.last_time}초 소요됨')
        self.last_name = name
        self.last_time = time.monotonic()

    def end(self):
        print(f'{DEBUG_HEAD}: {self.last_name} 틱 타이머 종료됨 - {time.monotonic() - self.last_time}초 소요됨')
        self.last_name = None
        

    