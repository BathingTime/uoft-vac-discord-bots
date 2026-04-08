'''Frodo Meet Constants
Author: Sunny Lin
Editors:
Last modified: Apr 7, 26

Constant variables to be imported and used in various other files.
'''
from common_bot_helper import read_json_file
from data_access import get_meetings
from meeting_time import MeetingTime

# Data file path:
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / 'meetings_data.json'


# Testing:
SAMPLE_MEETINGS_DATA = read_json_file('frodo-meet/meetings_data_sample.json')
SAMPLE_MEETINGS = get_meetings(SAMPLE_MEETINGS_DATA)
SAMPLE_NOW = MeetingTime.from_args(2025, 6, 7, 17, 55)
