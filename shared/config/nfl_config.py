import datetime
from typing import Dict, List, Optional

from shared.config.env import RAW_SCHEMA
from shared.config.queries import (
    CREATE_COMBINE_QUERY,
    CREATE_DEPTH_CHARTS_QUERY,
    CREATE_FTN_QUERY,
    CREATE_GAME_ODDS_QUERY,
    CREATE_INJURIES_QUERY,
    CREATE_NGS_PASSING_QUERY,
    CREATE_NGS_RECEIVING_QUERY,
    CREATE_NGS_RUSHING_QUERY,
    CREATE_PFR_PASSING_QUERY,
    CREATE_PFR_RECEIVING_QUERY,
    CREATE_PFR_RUSHING_QUERY,
    CREATE_PLAY_BY_PLAY_QUERY,
    CREATE_PLAYERS_QUERY,
    CREATE_SNAPS_QUERY,
    CREATE_WEEKLY_QUERY,
    CREATE_WEEKLY_ROSTERS_QUERY,
)

this_year = int(datetime.datetime.now().year)


class NFLDataSourceConfig:
    def __init__(
        self,
        nfl_data_py_method: Optional[str],
        schema: str,
        create_query: str,
        table: str,
        constraints: List[str],
        current_s3_key: str,
    ):
        self.nfl_data_py_method = nfl_data_py_method
        self.schema = schema
        self.create_query = create_query
        self.table = table
        self.constraints = constraints
        self.current_s3_key = current_s3_key


config_map: Dict[str, NFLDataSourceConfig] = {
    "pbp": NFLDataSourceConfig(
        nfl_data_py_method="pbp",
        schema=RAW_SCHEMA,
        create_query=CREATE_PLAY_BY_PLAY_QUERY,
        table="play_by_play",
        constraints=["play_id", "game_id"],
        current_s3_key=f"play_by_play/{this_year}.csv",
    ),
    "players": NFLDataSourceConfig(
        nfl_data_py_method="players",
        schema=RAW_SCHEMA,
        create_query=CREATE_PLAYERS_QUERY,
        table="players",
        constraints=["esb_id", "gsis_id"],
        current_s3_key="players/players.csv",
    ),
    "weekly": NFLDataSourceConfig(
        nfl_data_py_method="weekly",
        schema=RAW_SCHEMA,
        create_query=CREATE_WEEKLY_QUERY,
        table="weekly",
        constraints=["player_id", "week", "season"],
        current_s3_key=f"weekly/{this_year}.csv",
    ),
    "injuries": NFLDataSourceConfig(
        nfl_data_py_method="injuries",
        schema=RAW_SCHEMA,
        create_query=CREATE_INJURIES_QUERY,
        table="injuries",
        constraints=["gsis_id", "season", "week", "team"],
        current_s3_key=f"injuries/{this_year}.csv",
    ),
    "combine": NFLDataSourceConfig(
        nfl_data_py_method="combine",
        schema=RAW_SCHEMA,
        create_query=CREATE_COMBINE_QUERY,
        table="combine",
        constraints=["player_name, season, draft_team", "pos"],
        current_s3_key="combine/combine.csv",
    ),
    "ngs_rushing": NFLDataSourceConfig(
        nfl_data_py_method="ngs_rushing",
        schema=RAW_SCHEMA,
        create_query=CREATE_NGS_RUSHING_QUERY,
        table="rushing_next_gen_stats",
        constraints=["player_gsis_id", "season", "week"],
        current_s3_key=f"rushing_next_gen_stats/{this_year}.csv",
    ),
    "ngs_receiving": NFLDataSourceConfig(
        nfl_data_py_method="ngs_receiving",
        schema=RAW_SCHEMA,
        create_query=CREATE_NGS_RECEIVING_QUERY,
        table="receiving_next_gen_stats",
        constraints=["player_gsis_id", "season", "week"],
        current_s3_key=f"receiving_next_gen_stats/{this_year}.csv",
    ),
    "ngs_passing": NFLDataSourceConfig(
        nfl_data_py_method="ngs_passing",
        schema=RAW_SCHEMA,
        create_query=CREATE_NGS_PASSING_QUERY,
        table="passing_next_gen_stats",
        constraints=["player_gsis_id", "season", "week"],
        current_s3_key=f"passing_next_gen_stats/{this_year}.csv",
    ),
    "depth_chart": NFLDataSourceConfig(
        nfl_data_py_method="depth_chart",
        schema=RAW_SCHEMA,
        create_query=CREATE_DEPTH_CHARTS_QUERY,
        table="depth_charts",
        constraints=[
            "gsis_id",
            "season",
            "week",
            "depth_position",
            "depth_team",
            "game_type",
            "formation",
            "club_code",
        ],
        current_s3_key=f"depth_charts/{this_year}.csv",
    ),
    "pfr_rushing": NFLDataSourceConfig(
        nfl_data_py_method="pfr_rushing",
        schema=RAW_SCHEMA,
        create_query=CREATE_PFR_RUSHING_QUERY,
        table="rushing_pro_football_reference",
        constraints=["pfr_game_id", "pfr_player_id"],
        current_s3_key=f"rushing_pro_football_reference/{this_year}.csv",
    ),
    "pfr_receiving": NFLDataSourceConfig(
        nfl_data_py_method="pfr_receiving",
        schema=RAW_SCHEMA,
        create_query=CREATE_PFR_RECEIVING_QUERY,
        table="receiving_pro_football_reference",
        constraints=["pfr_game_id", "pfr_player_id"],
        current_s3_key=f"receiving_pro_football_reference/{this_year}.csv",
    ),
    "pfr_passing": NFLDataSourceConfig(
        nfl_data_py_method="pfr_passing",
        schema=RAW_SCHEMA,
        create_query=CREATE_PFR_PASSING_QUERY,
        table="passing_pro_football_reference",
        constraints=["pfr_game_id", "pfr_player_id"],
        current_s3_key=f"passing_pro_football_reference/{this_year}.csv",
    ),
    "snaps": NFLDataSourceConfig(
        nfl_data_py_method="snaps",
        schema=RAW_SCHEMA,
        create_query=CREATE_SNAPS_QUERY,
        table="snaps",
        constraints=["pfr_game_id", "pfr_player_id"],
        current_s3_key=f"snaps/{this_year}.csv",
    ),
    "ftn": NFLDataSourceConfig(
        nfl_data_py_method=None,
        schema=RAW_SCHEMA,
        create_query=CREATE_FTN_QUERY,
        table="ftn",
        constraints=["ftn_game_id", "ftn_play_id"],
        current_s3_key=f"ftn/{this_year}.csv",
    ),
    "weekly_rosters": NFLDataSourceConfig(
        nfl_data_py_method=None,
        schema=RAW_SCHEMA,
        create_query=CREATE_WEEKLY_ROSTERS_QUERY,
        table="rosters",
        constraints=[
            "season",
            "week",
            "position",
            "full_name",
            "pfr_id",
            "status",
            "team",
        ],
        current_s3_key=f"rosters/{this_year}.csv",
    ),
    "odds": NFLDataSourceConfig(
        nfl_data_py_method="game_results",
        schema=RAW_SCHEMA,
        create_query=CREATE_GAME_ODDS_QUERY,
        table="odds",
        constraints=["insert_date", "game_id"],
        current_s3_key="odds/odds.csv",
    ),
    "player_ids": NFLDataSourceConfig(
        nfl_data_py_method=None,
        schema=RAW_SCHEMA,
        create_query="",
        table="player_ids",
        constraints=["mfl_id"],
        current_s3_key="player_ids/player_ids.csv",
    ),
}
