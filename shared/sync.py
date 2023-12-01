#!/usr/bin/python
import datetime
import gzip
from io import BytesIO, StringIO
from typing import Any

from shared.config.env import  RAW_SCHEMA
from shared.enums.file_type import FileType
from shared.config.nfl_config import config_map
from shared.repositories.csv_repo import DataFileRepo


# def clean_na(response):
#     df = pd.read_csv(BytesIO(response))
#     print("Removing NA and replacing with null in csv..")
#     df.replace("NA", None, inplace=True)
#     return df.to_csv(index=False)


# def clean_weekly(response):
#     df = pd.read_csv(BytesIO(response))
#     if "opponent_team" not in df.columns:
#         print("Cleaning weekly csv..")
#         df.insert(10, "opponent_name", np.nan)
#     return df.to_csv(index=False)


# def add_insert_date(response, date):
#     df = pd.read_csv(BytesIO(response))
#     df["insert_date"] = date
#     return df.to_csv(index=False)


class UpdateS3:
    def __init__(self, s3_repo: Any, s3_bucket: str):
        self.s3 = s3_repo
        self.csv_repo = DataFileRepo()
        self.this_year = int(datetime.datetime.now().year)
        self.s3_bucket = s3_bucket

    def initialize_s3(self):
        print("initializing s3..")
        self.insert_all_play_by_play_csvs()
        self.insert_all_players_csvs()
        self.insert_all_weekly_csvs()
        self.insert_all_combine_csvs()
        self.insert_all_injury_csvs()
        self.insert_all_ngs_rushing_csvs()
        self.insert_all_ngs_passing_csvs()
        self.insert_all_ngs_receiving_csvs()
        self.insert_all_depth_chart_csvs()
        self.insert_all_pfr_rushing_csvs()
        self.insert_all_pfr_passing_csvs()
        self.insert_all_pfr_receiving_csvs()
        self.insert_all_snaps_csvs()
        self.insert_all_game_odds_csvs()
        self.insert_all_ftn_csvs()
        self.insert_all_roster_csvs()
        self.insert_all_player_ids_csvs()

    def update_s3(self):
        print("updating s3 data..")
        self.insert_play_by_play_csv(self.this_year)
        self.insert_all_players_csvs()
        self.insert_weekly_csv(self.this_year)
        self.insert_all_combine_csvs()
        self.insert_injury_csv(self.this_year)
        self.insert_ngs_rushing_csv(self.this_year)
        self.insert_ngs_passing_csv(self.this_year)
        self.insert_ngs_receiving_csv(self.this_year)
        self.insert_depth_chart_csv(self.this_year)
        self.insert_pfr_rushing_csv(self.this_year)
        self.insert_pfr_passing_csv(self.this_year)
        self.insert_pfr_receiving_csv(self.this_year)
        self.insert_snaps_csv(self.this_year)
        self.insert_all_game_odds_csvs()
        self.insert_ftn_csv(self.this_year)
        self.insert_roster_csv(self.this_year)
        self.insert_all_player_ids_csvs()

    def run_transform_stored_proc(self):
        self.sql_loader.run_stored_proc("transform_raw_data()")

    def insert_play_by_play_csv(self, year):
        nfl_config = config_map.get("pbp")
        table_name = nfl_config.table
        print(f"Extracting all play by play data from NflVerse for year: {year}")
        response = self.csv_repo.get_play_by_play(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_play_by_play_csvs(self):
        for year in range(1999, self.this_year + 1):
            self.insert_play_by_play_csv(year)

    def insert_all_players_csvs(self):
        nfl_config = config_map.get("players")
        table_name = nfl_config.table
        print("Extracting all players data from NflVerse")
        response = self.csv_repo.get_players()
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{table_name}.csv", Body=response)

    def insert_weekly_csv(self, year):
        nfl_config = config_map.get("weekly")
        table_name = nfl_config.table
        response = self.csv_repo.get_weekly(year)
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{year}.csv",
            Body=response,
        )

    def insert_all_weekly_csvs(self):
        for year in range(1999, self.this_year + 1):
            self.insert_weekly_csv(year)

    def insert_injury_csv(self, year):
        nfl_config = config_map.get("injuries")
        table_name = nfl_config.table
        response = self.csv_repo.get_injuries(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_injury_csvs(self):
        for year in range(2009, self.this_year + 1):
            self.insert_injury_csv(year)

    def insert_all_combine_csvs(self):
        nfl_config = config_map.get("combine")
        table_name = nfl_config.table
        response = self.csv_repo.get_combine()
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{table_name}.csv", Body=response)

    def insert_ngs_rushing_csv(self, year):
        nfl_config = config_map.get("ngs_rushing")
        table_name = nfl_config.table
        response = self.csv_repo.get_ngs_rushing(year)
        with BytesIO(response) as gzip_buffer:
            with gzip.GzipFile(fileobj=gzip_buffer, mode="rb") as f:
                decompressed_data = f.read()
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{year}.csv",
            Body=decompressed_data,
        )

    def insert_all_ngs_rushing_csvs(self):
        for year in range(2016, self.this_year + 1):
            self.insert_ngs_rushing_csv(year)

    def insert_ngs_passing_csv(self, year):
        nfl_config = config_map.get("ngs_passing")
        table_name = nfl_config.table
        response = self.csv_repo.get_ngs_passing(year)
        with BytesIO(response) as gzip_buffer:
            with gzip.GzipFile(fileobj=gzip_buffer, mode="rb") as f:
                decompressed_data = f.read()
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{year}.csv",
            Body=decompressed_data,
        )

    def insert_all_ngs_passing_csvs(self):
        for year in range(2016, self.this_year + 1):
            self.insert_ngs_passing_csv(year)

    def insert_ngs_receiving_csv(self, year):
        nfl_config = config_map.get("ngs_receiving")
        table_name = nfl_config.table
        response = self.csv_repo.get_ngs_receiving(year, FileType.GZIPPED)
        with BytesIO(response) as gzip_buffer:
            with gzip.GzipFile(fileobj=gzip_buffer, mode="rb") as f:
                decompressed_data = f.read()
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{year}.csv",
            Body=decompressed_data,
        )

    def insert_all_ngs_receiving_csvs(self):
        for year in range(2016, self.this_year + 1):
            self.insert_ngs_receiving_csv(year)

    def insert_depth_chart_csv(self, year):
        nfl_config = config_map.get("depth_chart")
        table_name = nfl_config.table
        response = self.csv_repo.get_depth_charts(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_depth_chart_csvs(self):
        for year in range(2001, self.this_year + 1):
            self.insert_depth_chart_csv(year)

    def insert_pfr_receiving_csv(self, year):
        nfl_config = config_map.get("pfr_receiving")
        table_name = nfl_config.table
        response = self.csv_repo.get_pfr_receiving(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_pfr_receiving_csvs(self):
        for year in range(2018, self.this_year + 1):
            self.insert_pfr_receiving_csv(year)

    def insert_pfr_rushing_csv(self, year):
        nfl_config = config_map.get("pfr_rushing")
        table_name = nfl_config.table
        response = self.csv_repo.get_pfr_rushing(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_pfr_rushing_csvs(self):
        for year in range(2018, self.this_year + 1):
            self.insert_pfr_rushing_csv(year)

    def insert_pfr_passing_csv(self, year):
        nfl_config = config_map.get("pfr_passing")
        table_name = nfl_config.table
        response = self.csv_repo.get_pfr_passing(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_pfr_passing_csvs(self):
        for year in range(2018, self.this_year + 1):
            self.insert_pfr_passing_csv(year)

    def insert_snaps_csv(self, year):
        nfl_config = config_map.get("snaps")
        table_name = nfl_config.table
        response = self.csv_repo.get_snaps(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_snaps_csvs(self):
        for year in range(2012, self.this_year + 1):
            self.insert_snaps_csv(year)

    def insert_ftn_csv(self, year):
        nfl_config = config_map.get("ftn")
        table_name = nfl_config.table
        response = self.csv_repo.get_ftn(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_ftn_csvs(self):
        for year in range(2022, self.this_year + 1):
            self.insert_ftn_csv(year)

    def insert_roster_csv(self, year):
        nfl_config = config_map.get("weekly_rosters")
        table_name = nfl_config.table
        response = self.csv_repo.get_weekly_rosters(year)
        self.s3.put_object(Bucket=self.s3_bucket, Key=f"{table_name}/{year}.csv", Body=response)

    def insert_all_roster_csvs(self):
        for year in range(2002, self.this_year + 1):
            self.insert_roster_csv(year)

    def insert_all_game_odds_csvs(self):
        nfl_config = config_map.get("odds")
        table_name = nfl_config.table
        response = self.csv_repo.get_game_odds()
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{table_name}.csv",
            Body=response,
        )

    def insert_all_player_ids_csvs(self):
        nfl_config = config_map.get("player_ids")
        table_name = nfl_config.table
        response = self.csv_repo.get_player_ids()
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=f"{table_name}/{table_name}.csv",
            Body=response,
        )

    def initialize_db(self):
        print("initializing db..")
        self.sql_loader.create_schema(RAW_SCHEMA)
        self.sql_loader.create_schema(RAW_SCHEMA)

        for key, nfl_config in config_map.items():
            print(f"Creating tables and inserting data for: {key}")

            schema = nfl_config.schema
            table_name = nfl_config.table
            constraints = nfl_config.constraints
            create_query = nfl_config.create_query

            self.sql_loader.execute_query(create_query)
            self.sql_loader.create_temporary_table(schema, table_name)
            self._copy_all_season_csvs_from_s3_to_postgres(schema, table_name, constraints)


    def _upload_dataframe_to_s3(self, df, s3_key):
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload the CSV data to S3 with the year-specific key
        self.s3.put_object(Bucket=self.s3_bucket, Key=s3_key, Body=csv_buffer.getvalue())

    def _upload_dataframe_to_s3_by_season(self, df, s3_table):
        print(f"Uploading data to s3 for table: {s3_table}")

        if "season" not in df.columns:
            print("Data is not seasonal, inserting directly")
            self._upload_dataframe_to_s3(df, s3_table + ".csv")
            return

        for year, group_df in df.groupby("season"):
            # Define the S3 key with the year as part of the path
            s3_key = f"{s3_table}/{int(year)}.csv"
            # Convert the grouped DataFrame to CSV format as a string
            self._upload_dataframe_to_s3(group_df, s3_key)

            print(f"DataFrame for year {year} uploaded as CSV to 's3://{self.s3_bucket}/{s3_key}' successfully")
