import datetime

import http.client
import ssl
from urllib.parse import urlparse
from shared.enums.file_type import FileType

GITHUB_HOST_NAME = 'github.com'

class DataFileRepo:
    def __init__(self):
        self.this_year = int(datetime.datetime.now().year)

    def get_play_by_play(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_players(self, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/players/players.{file_extension.value}"

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_weekly(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/player_stats/player_stats_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_injuries(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/injuries/injuries_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_combine(self, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = (
            f"/nflverse/nflverse-data/releases/download/combine/combine.{file_extension.value}"
        )

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_ngs_rushing(self, year: int, file_extension: FileType = FileType.GZIPPED):
        if file_extension not in FileType or file_extension == FileType.CSV:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/nextgen_stats/ngs_{year}_rushing.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_ngs_passing(self, year: int, file_extension: FileType = FileType.GZIPPED):
        if file_extension not in FileType or file_extension == FileType.CSV:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/nextgen_stats/ngs_{year}_passing.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_ngs_receiving(self, year: int, file_extension: FileType = FileType.GZIPPED):
        if file_extension not in FileType or file_extension == FileType.CSV:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/nextgen_stats/ngs_{year}_receiving.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_depth_charts(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/depth_charts/depth_charts_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_pfr_receiving(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/pfr_advstats/advstats_week_rec_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_pfr_passing(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/pfr_advstats/advstats_week_pass_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_pfr_rushing(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/pfr_advstats/advstats_week_rush_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_snaps(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_ftn(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/ftn_charting/ftn_charting_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_weekly_rosters(self, year: int, file_extension: FileType = FileType.CSV):
        if file_extension not in FileType:
            raise ValueError("Invalid FileType")

        path = f"/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_{year}.{file_extension.value}"  

        return self._get_file(GITHUB_HOST_NAME, path)

    def get_game_odds(self):
        return self._get_file("nflgamedata.com", "/games.csv")

    def get_player_ids(self):
        return self._get_file("raw.githubusercontent.com", "/dynastyprocess/data/master/files/db_playerids.csv")

    def _get_file(self, hostname, path, max_redirects=5):
        print(f"Requesting data for host: {hostname} path: {path}")

        if max_redirects <= 0:
            raise Exception("Too many redirects")

        conn = http.client.HTTPSConnection(hostname, context=ssl.create_default_context())
        conn.request("GET", path)

        response = conn.getresponse()
        print("Status:", response.status, response.reason)

        if response.status == 200:
            data = response.read()
            conn.close()
            return data
        
        elif response.status == 302:
            new_location = response.getheader('Location')
            print(f"Redirecting to {new_location}")

            conn.close()

            # Parse the new location URL for hostname and path
            new_url = urlparse(new_location)
            new_hostname = new_url.netloc
            new_path = new_url.path
            if new_url.query:
                new_path += '?' + new_url.query

            # Recursively call _get_file with the new URL
            return self._get_file(new_hostname, new_path, max_redirects - 1)
        
        else:
            conn.close()
            raise Exception(f"Request failed with status: {response.status}, {response.reason}")