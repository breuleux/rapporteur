import socket
import time
import traceback
from dataclasses import dataclass

from serieux.features.encrypt import Secret
from slack_sdk import WebClient

from .report import Report, Reporter
from .utils import readable_time


@dataclass(kw_only=True)
class SlackReporter(Reporter):
    token: Secret[str]
    channel: str
    show_logs: int = 15

    def __post_init__(self):
        self.client = WebClient(token=self.token)

    def log(self, markdown: str = None, **kwargs):
        self.client.chat_postMessage(
            channel=self.channel,
            markdown_text=markdown,
            **kwargs,
        )

    def report(self, report: Report):
        duration_str = readable_time(report.end - report.start)

        success = not report.exception
        sprefix = "" if success else "un"

        icons = ""
        if n := report.statistics["log_warning"]:
            icons += f" ⚠️{n}"
        if n := report.statistics["log_error"]:
            icons += f" ❌{n}"

        blocks = []
        exception = report.exception
        if exception is not None:
            icons += f" (**raised** {type(exception).__name__})"
            tb_str = "".join(
                traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                )
            )[-2900:]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Exception traceback:*\n```{tb_str}```",
                    },
                }
            )
        if report.errlogs and (nerr := self.show_logs):
            error_lines = []
            for record in list(report.errlogs)[-nerr:]:
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
                msg = record.getMessage()
                error_lines.append(f"{ts} [{record.levelname}] {record.name}: {msg}")
            error_block = "\n".join(error_lines)[-2900:]
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Last {nerr} errors logged:*\n```{error_block}```",
                    },
                }
            )

        hostname = socket.gethostname()
        summary = f"[{hostname}] **{report.description}** ran **{sprefix}successfully** in {duration_str}. {icons}"

        self.client.chat_postMessage(
            channel=self.channel,
            markdown_text=summary,
            attachments=[{"blocks": blocks, "fallback": "<error summary>"}],
            icon_emoji=(
                ":x:"
                if exception
                else (":warning:" if report.errlogs else ":white_check_mark:")
            ),
        )
