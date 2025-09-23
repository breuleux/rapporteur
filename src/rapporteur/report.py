import logging
from collections import deque
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from logging import LogRecord
from typing import Counter

from .config import config
from .utils import LogHook


@dataclass
class Report:
    description: str = None
    start: datetime = None
    end: datetime = None
    statistics: Counter = field(default_factory=Counter)
    errlogs: deque[LogRecord] = field(
        default_factory=lambda: deque(maxlen=config.keep_logs)
    )
    exception: Exception = None

    def on_log(self, lrec: LogRecord):
        self.statistics["log_" + lrec.levelname.lower()] += 1
        if lrec.levelno >= logging.ERROR:
            self.errlogs.append(lrec)

    @contextmanager
    def run(self, *reporters):
        assert reporters
        self.start = datetime.now()
        with LogHook(self.on_log):
            try:
                for r in reporters:
                    r.pre_report(self)
                yield self
            except Exception as exc:
                self.exception = exc
                raise
            finally:
                self.end = datetime.now()
                for r in reporters:
                    r.report(self)
