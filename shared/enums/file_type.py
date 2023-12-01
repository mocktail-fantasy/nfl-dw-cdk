from enum import Enum


class FileType(Enum):
    CSV = "csv"
    GZIPPED = "csv.gz"
    PARQUET = "parquet"
