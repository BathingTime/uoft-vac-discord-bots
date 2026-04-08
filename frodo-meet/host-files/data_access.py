'''Frodo Meet Data Access
Author: Sunny Lin
Editors:
Last modified: Apr 6, 26

Functions to fetch from and write to files data.
'''
import common_bot_helper
from meeting import Meeting


# HELPER FUNCTIONS:

def get_meetings(file_data: dict) -> list[Meeting]:
    '''
    Given the data from a json file, construct and return a list of Meeting objects.


    Sample Usage:
    >>> from constants import SAMPLE_MEETINGS_DATA

    >>> meetings = get_meetings(SAMPLE_MEETINGS_DATA)
    >>> meeting1 = meetings[0]

    >>> meeting1.get_title()
    'General Meeting 1'

    >>> meeting1.get_time().get_timestamp()
    1749319200.0

    >>> meeting1.get_description()
    'Our first exec meeting of the year! Get to know each other and a run down on club operations.'

    >>> meeting1.get_participants()
    ['<r>11111']

    >>> meeting1.get_labels()
    ['soon']

    >>> meeting2 = meetings[1]

    >>> meeting2.get_title()
    'Weekly Event Recap'

    >>> meeting2.get_time().get_timestamp()
    1749837600.0

    >>> meeting2.get_description()
    "Go over today's event. How did it go, anything nice, any improvements for the future, etc."

    >>> meeting2.get_participants()
    ['<r>22222']

    >>> meeting2.get_labels()
    ['weekly', 'paused']
    '''
    return [Meeting.from_file(entry_data) for entry_data in file_data['meetings']]


def write_meetings(file_path: str, meetings: list[Meeting]) -> None:
    '''
    Given a list of Meeting objects, write the data to the json file.

    Sample usage inapplicable.
    '''
    common_bot_helper.write_json_file(file_path, {'meetings': [{
        'title': meeting.get_title(),
        'time': meeting.get_time().get_timestamp(),
        'description': meeting.get_description(),
        'participants': meeting.get_participants(),
        'labels': meeting.get_labels(),
    } for meeting in meetings]})


if __name__ == '__main__':
    from doctest import testmod
    testmod()
