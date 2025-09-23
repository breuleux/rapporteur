import socket
import time
import traceback
from dataclasses import dataclass, field

import gifnoc
from serieux.features.encrypt import Secret
from slack_sdk import WebClient

from .report import Report
from .utils import readable_time


@dataclass
class SlackConfig:
    token: Secret[str]
    show_logs: int = 15
    channel_map: dict[str, str] = field(default_factory=dict)


class SlackReporter:
    def __init__(self, channel):
        self.client = WebClient(token=slack.token)
        self.channel = slack.channel_map.get(channel, channel)

    def pre_report(self, report: Report):
        pass

    def status(self, markdown_text: str = None, **kwargs):
        self.client.chat_postMessage(
            channel=self.channel,
            markdown_text=markdown_text,
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
        if report.errlogs:
            nerr = slack.show_logs
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


slack = gifnoc.define("rapporteur.slack", SlackConfig)
