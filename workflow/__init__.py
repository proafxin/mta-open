# fmt: off
from dagster import Definitions, load_assets_from_modules

from workflow.assets import crashes, metrics

crash_assets = load_assets_from_modules([crashes])
metric_assets = load_assets_from_modules([metrics])

defs = Definitions(assets=[*crash_assets, *metric_assets])
