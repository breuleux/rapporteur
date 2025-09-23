
# Rapporteur

A simple package to log the result of the execution of a program, as well as status updates, to Slack (and possibly other backends).


## Getting the information you need

To make rapporteur work, you need:

1. A Slack app installed in the workspace (https://api.slack.com/apps). Make sure that it has the scope to write to channels, and add it to the relevant channels.
2. A token for that app. You can find it in OAuth&Permissions
3. The channel ID. If you click on the name of a channel, you can see its Channel ID at the bottom, which typically starts with C. If you are in a browser, it is also the last part of the URL.


## Basic usage

```python
from rapporteur.report import Report
from rapporteur.slack import SlackReporter

report = Report(
    description="My test report",
    reporters=[
        SlackReporter(token="xoxb-your-token", channel="C12345678")
    ],
)
with report:
    logger.info("Hello, world!")
    logger.error("oh no!")  # Will be in the Slack report
```


## With serieux

The configuration for a report can be stored in a file and deserialized using serieux (>=0.2.9).

**Configuration**

```yaml
description: "test test test"
reporters:
  - $class: rapporteur.slack:SlackReporter
    token: "xoxb-your-token"
    show_logs: 5   # Show last 5 error logs
    channel: "C12345678"
```

To encrypt the token using PASSWORD, set the `$SERIEUX_PASSWORD` environment variable to PASSWORD and run:

```bash
serieux patch -m rapporteur.report:Report -f path/to/config.yaml
```

The above command will patch the config inplace to replace the token with an encrypted version of the token, using the provided password. The argument to `-m` is a reference to the model for the whole configuration file, so you may want to adjust it if the report config is part of a bigger config.

**Code**

```python
import os
from serieux import deserialize
from serieux.features.encrypt import EncryptionKey

# You can omit EncryptionKey if it's not encrypted
report = deserialize(Report, Path("path/to/config.yaml"), EncryptionKey(os.environ[SERIEUX_PASSWORD]))
with report:
    logger.info("Hello, world!")
    logger.error("oh no!")  # Will be in the Slack report
```
