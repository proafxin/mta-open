from enum import Enum


class Option(str, Enum):
    YEAR = "year"
    MONTH = "month"
    HOUR = "hour"
    DATE = "date"


options = [Option.DATE.value, Option.YEAR.value, Option.MONTH.value, Option.HOUR.value]
