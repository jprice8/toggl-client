import os
from typing import Any, Dict, List

import requests


class Endpoints:
    """
    Enum style endpoints for Toggl API.
    """
    DETAILED_REPORT = "https://api.track.toggl.com/reports/api/v2/details"


class TogglClient:
    """
    A client to interact with the Toggl API.
    """
    def __init__(self):
        self.headers = {
            "Authorization": "",
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "python/requests"
        }
        self.user_agent = ""

    #### Set headers ####

    def setAPIKey(self, APIKey: str) -> None:
        """
        Set user API key for request.
        """
        authHeader = APIKey + ":api_token"
        self.headers['Authorization'] = authHeader

    def setUserAgent(self, agent: str) -> None:
        """
        Set user agent for request.
        """
        self.user_agent = agent

    #### Methods for report data ####
    def getDetailedReport(self, session: requests.Session, payload: Dict[str, str]) -> Dict[str, Any]:
        """
        Make a request to the detailed data report.

        Reponse will be in JSON format.
        """
        # Add user agent to parameters
        payload['user_agent'] = self.user_agent
        r = session.get(Endpoints.DETAILED_REPORT, headers=self.headers, params=payload)
        return r.json()


if __name__ == '__main__':
    togglClient = TogglClient()

    # Set headers
    togglClient.setAPIKey(os.getenv('APIKEY'))
    togglClient.setUserAgent('TimeTrackerDashboard')

    # Instantiate Session object . Session object allows us to 
    # persist parameters across requests.
    session = requests.Session()

    session.auth = (os.getenv('APIKEY'), 'api_token')

    # Make request
    payload = {
        'workspace_id': '5997219',
        'since': '2022-01-29',
        'until': '2022-01-29'
    }

    print(togglClient.getDetailedReport(session, payload))
