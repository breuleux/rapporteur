import logging


class HookHandler(logging.Handler):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def emit(self, record):
        self.fn(record)


class LogHook:
    def __init__(self, fn):
        self.handler = HookHandler(fn)
        self.logger = logging.getLogger()

    def __enter__(self):
        self.logger.addHandler(self.handler)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.removeHandler(self.handler)


def readable_time(duration):
    duration = int(duration.total_seconds())
    if duration == 0:
        return "<1s"
    elif duration < 60:
        return f"{duration}s"
    elif duration < 3600:
        mins = int(duration // 60)
        secs = duration % 60
        return f"{mins}m {secs}s"
    else:
        hours = int(duration // 3600)
        mins = int((duration % 3600) // 60)
        secs = duration % 60
        return f"{hours}h {mins}m {secs}s"
