import threading
import time

# 업로드/처리 진행상태를 저장할 dict (메모리 기반, 프로덕션은 Redis 등 사용 권장)
progress_dict = {}

class ProgressTracker:
    def __init__(self, task_id):
        self.task_id = task_id
        self.progress = 0
        self.status = "processing"
        self.message = "처리 중"
        self.lock = threading.Lock()
        progress_dict[task_id] = self

    def set_progress(self, value, message=None):
        with self.lock:
            self.progress = value
            if message:
                self.message = message
            if value >= 100:
                self.status = "done"
                self.message = "업로드 및 벡터 적재 완료"

    def set_error(self, message):
        with self.lock:
            self.status = "error"
            self.message = message
            self.progress = 0

    def get_status(self):
        with self.lock:
            return {
                "task_id": self.task_id,
                "progress": self.progress,
                "status": self.status,
                "message": self.message
            }

def get_progress(task_id):
    tracker = progress_dict.get(task_id)
    if tracker:
        return tracker.get_status()
    return {"task_id": task_id, "progress": 0, "status": "unknown", "message": "진행 정보 없음"}
