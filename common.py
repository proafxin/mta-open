from enum import Enum


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"


options = [Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]
