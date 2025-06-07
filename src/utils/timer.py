import time
from functools import wraps

class Timer:
    """utility untuk mengukur waktu eksekusi"""
    
    def __init__(self):
        self.start_time = None
        self.elapsed_time = None
    
    def start(self):
        """mulai timer"""
        self.start_time = time.perf_counter()
        self.elapsed_time = None
    
    def stop(self):
        """stop timer dan return elapsed time dalam milliseconds"""
        if self.start_time is None:
            raise RuntimeError("Timer belum dimulai")
        
        end_time = time.perf_counter()
        self.elapsed_time = (end_time - self.start_time) * 1000  # convert ke ms
        self.start_time = None
        
        return self.elapsed_time
    
    def get_elapsed(self):
        """ambil elapsed time terakhir"""
        if self.elapsed_time is None:
            raise RuntimeError("Timer belum berjalan atau belum distop")
        return self.elapsed_time
    
    def reset(self):
        """reset timer"""
        self.start_time = None
        self.elapsed_time = None
    
    @staticmethod
    def measure(func):
        """decorator untuk otomatis mengukur waktu eksekusi fungsi"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            timer = Timer()
            timer.start()
            
            try:
                result = func(*args, **kwargs)
                elapsed = timer.stop()
                
                # tambahkan waktu eksekusi ke result jika dict
                if isinstance(result, dict):
                    result['execution_time_ms'] = elapsed
                
                return result
            except Exception as e:
                timer.stop()
                raise e
        
        return wrapper
    
    @staticmethod
    def format_time(milliseconds):
        """format waktu ke string yang readable"""
        if milliseconds < 1000:
            return f"{milliseconds:.0f}ms"
        else:
            seconds = milliseconds / 1000
            return f"{seconds:.2f}s"

class BlockTimer:
    """context manager untuk timing code blocks"""
    
    def __init__(self, name="Block"):
        self.name = name
        self.timer = Timer()
    
    def __enter__(self):
        self.timer.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = self.timer.stop()
        print(f"{self.name} execution time: {Timer.format_time(elapsed)}")
        return False
    
    def get_elapsed(self):
        return self.timer.get_elapsed()