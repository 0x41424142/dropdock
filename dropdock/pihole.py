"""
Contains pihole API interaction code
"""
from typing import Literal
from urllib3 import disable_warnings
from json import dumps

from requests import get, post, delete

from .models import PiHoleGroup, PiHoleGroupList, PiHoleDomain, PiHoleDomainList
from .logger import setup_logging

# Set up logging
logger = setup_logging()

disable_warnings()

class PiHole:
    """
    Class to interact with the Pi-hole API.
    """
    
    def __init__(self, base_url: str = "https://pi.hole/api", password: str = None):
        """
        Initialize the PiHole class with base URL, username, and password.
        
        :param base_url: The base URL of the Pi-hole API.
        :param password: The password for authentication.
        """
        self.base_url = base_url
        self.password = password
        self._sid = None
        self.initialize_session()
        
    def __repr__(self):
        return f"PiHole(base_url={self.base_url}, password=****)"
    
    def __str__(self):
        return self.base_url
    
    @property
    def is_authenticated(self):
        """
        Check if the session is authenticated.
        
        :return: True if authenticated, False otherwise.
        """
        return self._sid is not None
    
    @property
    def sid(self):
        """
        Returns the SID as a header dict
        """
        return {"sid": self._sid}
        
    def initialize_session(self):
        """
        Initialize a session with the Pi-hole API.
        """
        url_path = "/auth"
        r = get(f"{self.base_url}{url_path}", verify=False)
        if not r.json()["session"]["valid"]:
            # Auth required
            authenticate = post(f"{self.base_url}{url_path}", json={"password": self.password}, verify=False)
            if jsn:= authenticate.json():
                if jsn["session"]["valid"]:
                    self._sid = jsn["session"]["sid"]
                else:
                    logger.info(f"Authentication failed: {jsn['session']['message']}")
                    raise Exception(f"Authentication failed:{jsn["session"]["message"]}")
        else:
            if r.json()["session"]["sid"] != self._sid:
                self._sid = r.json()["session"]["sid"]
                
    def make_call(self, url_path: str, method: Literal["GET", "POST", "DELETE"], params: dict = None, payload: dict = None) -> dict:
        """
        Make a call to the Pi-hole API.
        
        :param url_path: The URL path for the API endpoint.
        :param method: The HTTP method to use (GET, POST, DELETE).
        :param params: The query parameters for the request.
        :param payload: The payload for POST requests.
        :return: The response from the API.
        """
        
        url = f"{self.base_url}{url_path}"
        # convenience:
        method = method.upper()
        
        if method == "GET":
            r = get(url, headers=self.sid, params=params, verify=False)
        elif method == "POST":
            r = post(url, headers=self.sid, json=payload, params=params, verify=False)
        elif method == "DELETE":
            r = delete(url, headers=self.sid, params=params, verify=False)
        else:
            logger.info(f"Invalid HTTP method: {method}")
            raise ValueError("Invalid HTTP method")
        
        if r.status_code not in [200, 201, 204]:
            logger.info(f"Error: {r.status_code}:\n{dumps(r.json(), indent=2)}")
            raise Exception(f"Error: {r.status_code}:\n{dumps(r.json(), indent=2)}")
        logger.debug(f"Made {method} call to {url} with params {params} and payload {payload}")
        return r.json() if len(r.content) > 0 else {}
    
    def get_groups(self, group_name: str | list[str] = None) -> PiHoleGroupList:
        """
        Get the list of groups from the Pi-hole API.
        
        :param group_name: The name of the group to retrieve. If None, all groups are retrieved.
        
        :return: The list of groups.
        """
        url_path = "/groups"
        
        if isinstance(group_name, str):
            group_name = [group_name]
        elif not group_name:
            group_name = ' ' #dummy value to get all groups
            
        ls = PiHoleGroupList(groups=[])
        for name in group_name:
            r = self.make_call(
                url_path + f"/{name}" if name != ' ' else url_path,
                "GET"
            )
            ls.groups.extend([PiHoleGroup(**group) for group in r["groups"]])
        return ls
        
    def get_domains(self, filter_by: Literal["comment", "id", "name", "enabled", None] = None, filter_value: str | None = None) -> list[dict]:
        """
        Get the list of domains from the Pi-hole API.
        
        :param filter_by: The filter to apply to the domains. Can be "comment", "id", "name", "enabled", or None.
        :param filter_value: The value to filter by. If None, all domains are retrieved.
        
        :return: The list of domains.
        """
        if filter_by not in ["comment", "id", "name", "enabled", None]:
            raise ValueError("Invalid filter_by value. Must be one of: comment, id, name, enabled, None")
        
        url_path = "/domains"
        dlist = PiHoleDomainList(domains=[])
        data = self.make_call(
            url_path,
            "GET",
        )
    
        dlist.domains = [PiHoleDomain.model_validate(domain) for domain in data["domains"]]
        if filter_by and filter_value:
            dlist.domains = [domain for domain in dlist.domains if getattr(domain, filter_by) == filter_value]
        return dlist.domains