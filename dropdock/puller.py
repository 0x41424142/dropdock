"""
Pulls data from Spamhaus DROP
"""

from requests import get
from json import loads

from .models import DROPEntry
    

def pull_data():
    """
    Pulls data from Spamhaus DROP
    """
    url = "https://www.spamhaus.org/drop/asndrop.json"
    response = get(url)
    response.raise_for_status()
    # At this point the response is a JSON string 
    # containing newline-separated objects
    # drop the last str in the list, which contains metadata
    data = response.text.splitlines()[:-1]
    data = [DROPEntry(**loads(line)) for line in data if line ]
    return data
    
    