'''Frodo Meet - Helper
'''
from meeting import Meeting


def show_meetings(filters: tuple[str], meetings: list[Meeting], ids_to_names: dict[str: str]) -> str:
    '''
    Display the meetings list in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of active meetings.

    Filters can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings on record.
    - <label>: only display meetings of that label (multiple allowed).
    - <index>: only display meetings of that index (mutliple allowed).
    - -<all/label/index>: do not display meetings relevant to -filters.

    Priority: index > label > all
    If a meeting has an filter label and another -filter label, it will still be displayed.

    Sample Usage:
    >>> from frodo_meet_data import SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES

    >>> show_meetings((), [], {})
    'No meetings exist on record. 🧐'
    
    >>> show_meetings((), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'

    >>> show_meetings(('full',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: Execs\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\nnotify: will not notify since marked as soon. begin: will begin, be removed, and be cloned tomorrow\\n__Participants__: Execs, Sunny\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)\\nwill not notify or begin\\n__No participants__ 🧐'

    >>> show_meetings(('all',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\n## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'
    
    >>> show_meetings(('all', '-soon', '-1'), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'

    >>> show_meetings(('-all',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    'No meetings of such specification exists. 🧐'

    >>> show_meetings(('-all', 'paused', '4'), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)'
    '''
    # print(meetings)

    if not meetings: return 'There are no meetings. 🧐'

    # Turn all args lowercase.
    filters = tuple(arg.lower() for arg in filters)

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If current entry is not to be displayed, skip.
        if not curr_meeting.to_display(meetings_i, filters): continue
        
        # Compute and add the output for the meeting.
        output += f'{curr_meeting.to_discord(meetings_i, 'full' in filters, ids_to_names)}\n'
    
    return output[:-1] if output else 'There are no meetings of such specification. 🧐'


def find_meeting(meetings: list[Meeting], target: str) -> Meeting | str:
    '''
    Given a target string, find a meeting in the meetings list.
    Return the meeting object if found, and an error message otherwise.

    A digit target string will be interpreted as an index (1-indexed):
    - Find the meeting at the corresponding 0-indexed index.
    A non-digit target string will be interpreted as a title:
    - Find the first meeting with the same title.
    
    Sample Usage:
    >>>
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

    >>> new_meeting = Meeting('new meeting', MeetingTime(5), 'will be inserted at index 3 (after past meetings)', [], [])

    >>> index = add_meeting(meetings, new_meeting)
    >>> index
    3

    >>> meetings[index].get_title()
    'new meeting'
    '''
    meetings.append(new_meeting)
    meetings.sort()

    return meetings.index(new_meeting)


def remove_meeting(meetings: list[Meeting], target_meeting: Meeting) -> str:
    '''
    Given a meeting, remove it from the meetings list.
    If the meeting is not in the meetings list, return an error message.
    This is possible for example if the meeting began while removing it.
    '''
    if not target_meeting in meetings:
        return f'It seems {target_meeting.get_title(True)} does not exist at the time of confirmation; nothing to delete. 🧐'

    meetings.remove(target_meeting)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
