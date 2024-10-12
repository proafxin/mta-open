from pathlib import Path

DATADIR = Path(__file__).parent.parent.parent / "data"
OUTDIR = Path(__file__).parent / "data"
if not OUTDIR.exists():
    OUTDIR.mkdir(parents=True, exist_ok=True)

STAGINGDIR = OUTDIR / "staging"
if not STAGINGDIR.exists():
    STAGINGDIR.mkdir(parents=True, exist_ok=True)

DUCKDB_LOCATION = STAGINGDIR / "data.duckdb"
VEHICLE_CRASH_FILENAME = "vehicle_crash.csv"
MOTOR_VEHICLES_COLLISION_FILENAME = "motor_vehicles_collisions.csv"
TAXI_ZONES_FILE_PATH = "data/raw/taxi_zones.csv"
TAXI_TRIPS_TEMPLATE_FILE_PATH = "data/raw/taxi_trips_{}.parquet"

TRIPS_BY_AIRPORT_FILE_PATH = "data/outputs/trips_by_airport.csv"
TRIPS_BY_WEEK_FILE_PATH = "data/outputs/trips_by_week.csv"
MANHATTAN_STATS_FILE_PATH = "data/staging/manhattan_stats.geojson"
MANHATTAN_MAP_FILE_PATH = "data/outputs/manhattan_map.png"

REQUEST_DESTINATION_TEMPLATE_FILE_PATH = "data/outputs/{}.png"

DATE_FORMAT = "%Y-%m-%d"

START_DATE = "2023-01-01"
END_DATE = "2023-04-01"
