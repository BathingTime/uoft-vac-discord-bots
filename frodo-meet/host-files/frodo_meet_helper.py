'''Frodo Meet - Helper
'''
from meeting import Meeting


def get_meetings_to_discord(
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    filters: tuple[str]
) -> str:
    '''
    Display the meetings list in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of all active meetings.

    Filters can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings.
    - soon, recurring, daily, weekly, yearly, active: display all meetings relevant to these filters (multiple allowed).
    - <index>: display all meetings of that index (multiple allowed).
    - -<filter>: do not display meetings relevant to -filters (multiple allowed).

    Priority: index > intermediate filters > all
    If a meeting is relevant to both a +filter and a -filter of the same priority, it WILL be displayed.

    Sample Usage:
    >>> from frodo_meet_data import SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES
    '''
    # print(meetings)

    if not meetings: return 'There are no meetings. 🧐'

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If meeting shouldn't be displayed, skip.
        if not curr_meeting.to_display(meetings_i, filters): continue
        
        # Add meeting to print.
        output += f'{curr_meeting.to_discord(
            index = meetings_i,
            full = 'full' in filters,
            ids_to_names = ids_to_names
        )}\n'
    
    return output if output else 'There are no meetings under such filters. 🧐'


def find_meeting(meetings: list[Meeting], target: str) -> Meeting | str:
    '''
    Given a target string, find a meeting in the meetings list.
    Return the meeting object if found, and an error message otherwise.

    A digit target string will be interpreted as an index (1-indexed):
    - Find the meeting at the corresponding 0-indexed index.
    A non-digit target string will be interpreted as a title:
    - Find the first meeting with the same title.
    
    Sample Usage:
    >>> from frodo_meet_data import SAMPLE_MEETINGS
    '''
    # If target is an index:
    if target.isdigit():
        index = int(target) - 1

        if not 0 <= index < len(meetings):
            return f'Given index is invalid; must be **1–{len(meetings)}**. 🧐'
        
        return meetings[index]
    
    # Otherwise, target is a title:
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        if curr_meeting.get_title().strip().lower() == target.strip().lower():
            return curr_meeting
    
    return 'There is no meeting with that title. 🧐'


def add_meeting(meetings: list[Meeting], new_meeting: Meeting) -> int:
    '''
    Add the new meeting to the meetings list, and sort it.
    Return the new meeting's index in the sorted list.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS

    >>> meetings = deepcopy(SAMPLE_MEETINGS)
    '''
    meetings.append(new_meeting)
    meetings.sort()

    return meetings.index(new_meeting)


def remove_meeting(meetings: list[Meeting], target_meeting: Meeting) -> str:
    '''
    Given a meeting, remove it from the meetings list.
    If the meeting is not in the meetings list, return an error message.
    This is possible, for example, if the meeting began while in the process of removing it.
    Otherwise, return None.
    '''
    if not target_meeting in meetings:
        return f'It seems {target_meeting.get_title(True)} does not exist at the time of confirmation. 🧐'
    
    meetings.remove(target_meeting)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
