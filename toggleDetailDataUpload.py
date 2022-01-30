#%%
import os
from typing import List
import datetime
import json

import pandas as pd
from sqlalchemy import create_engine
import requests

from TogglClient import TogglClient


class DetailData:
    """
    A class to represent the detail data actions.
    """
    def __init__(self):
        self.today = datetime.date.today()
        self.yesterday = self.today - datetime.timedelta(days=1)

    def fetch_data(self, since=None, until=None, workspace_id=None) -> pd.DataFrame:
        """
        Fetch detail data from toggl API. Default is to pull yesterday's
        data. Can pass since and until as time ranges. Make sure you pass
        arguments as strings in 'yyyy-mm-dd' format.
        """
        togglClient = TogglClient()

        # Set headers
        togglClient.setUserAgent('TimeTrackerDashboard')

        session = requests.Session()
        session.auth = (os.getenv('APIKEY'), 'api_token')

        # Get time range strings
        if since is None or until is None:
            since = str(self.yesterday)
            until = str(self.yesterday)

        if workspace_id is None:
            workspace_id = os.getenv('WORKSPACE_ID')

        payload = {
            'workspace_id': workspace_id,
            'since': since,
            'until': until
        }

        json_data = togglClient.getDetailedReport(session, payload)
        json_str = json.dumps(json_data['data'])
        df = pd.read_json(json_str, orient='records')

        # Clean data, change data types
        df.start = pd.to_datetime(df.start)
        df.end = pd.to_datetime(df.end)
        df.updated = pd.to_datetime(df.updated)

        return df


class Database:
    """
    A class to represent our SQL database.
    """
    def __init__(self):
        self.USER = os.getenv('DATABASE_USER')
        self.PASSWORD = os.getenv('DATABASE_PASSWORD')
        self.HOST = os.getenv('DATABASE_HOST')
        self.PORT = os.getenv('DATABASE_PORT')
        self.DATABASE_NAME = os.getenv('DATABASE_NAME')

        self.ENGINE = create_engine(
            f'postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE_NAME}'
        )

    def save(self, df: pd.DataFrame) -> str:
        """
        Save dataframe to database table.
        """
        df.to_sql(
            'detail',
            con=self.ENGINE,
            if_exists='append',
            index=False
        )
        return f'Successfully uploaded {len(df)} rows to the detail table!'

    def check_for_preexisting_entries(self, df_to_load: pd.DataFrame) -> pd.DataFrame:
        """
        Compare the time entry ID's of the dataframe to load against past entries.
        
        If there are matching ID's, return True to prevent uploading.
        """
        past_entries_df = pd.read_sql_table('detail', self.ENGINE)
        ids_to_upload = df_to_load['id']
        matching_id_df = past_entries_df[past_entries_df['id'].isin(ids_to_upload)]
        return len(matching_id_df) > 0


if __name__ == '__main__':
    detailData = DetailData()
    df = detailData.fetch_data()

    database = Database()
    if database.check_for_preexisting_entries(df):
        print('You are trying to upload a preexisting time entry.')
    else:
        print(database.save(df))
