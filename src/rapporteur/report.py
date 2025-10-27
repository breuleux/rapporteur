from __future__ import annotations

import logging
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime
from logging import LogRecord

from serieux import TaggedSubclass

from .utils import LogHook


@dataclass
class Report:
    description: str
    reporters: list[TaggedSubclass[Reporter]]

    def __post_init__(self):
        self.start: datetime = None
        self.end: datetime = None
        self.statistics: Counter = Counter()
        self.errlogs: deque[LogRecord] = deque(maxlen=1000)
        self.exception: Exception = None

    def on_log(self, lrec: LogRecord):
        self.statistics["log_" + lrec.levelname.lower()] += 1
        if lrec.levelno >= logging.ERROR:
            self.errlogs.append(lrec)

    def __enter__(self):
        self.start = datetime.now()
        self._loghook = LogHook(self.on_log)
        self._loghook.__enter__()
        for r in self.reporters:
            r.pre_report(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.exception = exc_val
        self.end = datetime.now()
        for r in self.reporters:
            r.report(self)
        self._loghook.__exit__(exc_type, exc_val, exc_tb)
        return False


class Reporter:
    def log(self, markdown: str):
        raise NotImplementedError()

    def pre_report(self, report: Report):
        # OK if not implemented
        pass

    def report(self, report: Report):
        raise NotImplementedError()
