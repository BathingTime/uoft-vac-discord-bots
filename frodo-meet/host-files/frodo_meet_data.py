'''Frodo Meet - Data

Functions to fetch from and write to files data.
'''
from pathlib import Path

from common_bot_helper import read_json_file, write_json_file

from meeting import Meeting,\
    ATTRIBUTE_TITLE,\
    ATTRIBUTE_TIME,\
    ATTRIBUTE_DESCRIPTION,\
    ATTRIBUTE_PARTICIPANTS,\
    ATTRIBUTE_RECURRENCE,\
    ATTRIBUTE_ACTIVE,\
    ATTRIBUTE_SOON
from meeting_time import MeetingTime


MEETINGS_FILE_KEY = 'meetings'

# Data file path
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / 'meetings_data.json'

# Sample data
SAMPLE_MEETINGS_DATA = read_json_file('frodo-meet/meetings_data_sample.json')
EPOCH = MeetingTime(0)
SAMPLE_IDS_TO_NAMES = {
    '12345': 'Execs',
    '67890': 'Sunny'
}


def get_meetings(file_data: dict) -> list[Meeting]:
    return [Meeting.from_file(entry_data) for entry_data in file_data[MEETINGS_FILE_KEY]]

SAMPLE_MEETINGS = get_meetings(SAMPLE_MEETINGS_DATA) # Sample data


def write_meetings(file_path: str, meetings: list[Meeting]) -> None:
    write_json_file(file_path, {MEETINGS_FILE_KEY: [{
        ATTRIBUTE_TITLE: meeting.get_title(),
        ATTRIBUTE_TIME: meeting.get_time().get_timestamp(),
        ATTRIBUTE_DESCRIPTION: meeting.get_description(),
        ATTRIBUTE_PARTICIPANTS: meeting.get_participants(),
        ATTRIBUTE_RECURRENCE: meeting.get_recurrence(),
        ATTRIBUTE_ACTIVE: meeting.get_active(),
        ATTRIBUTE_SOON: meeting.get_soon()
    } for meeting in meetings]})


if __name__ == '__main__':
    from doctest import testmod
    testmod()
