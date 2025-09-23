import gifnoc


class RapporteurConfig:
    keep_logs: int = 1000


config = gifnoc.define("rapporteur", RapporteurConfig)
