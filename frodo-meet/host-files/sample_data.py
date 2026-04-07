'''Sample Data
Author: Sunny Lin
Editors:
Last modified: Apr 7, 26

Constant variables to be imported and used in other files for testing.
'''
from common_bot_helper import read_json_file
from data_access import get_meetings
from meeting_time import MeetingTime


SAMPLE_ENTRIES_DATA = read_json_file('frodo-meet/meeting_entries_sample.json')

SAMPLE_MEETINGS = get_meetings(SAMPLE_ENTRIES_DATA)

SAMPLE_NOW = MeetingTime.from_args(2025, 6, 7, 17, 55)
