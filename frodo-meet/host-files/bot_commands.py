'''Frodo Meet Bot Commands
Author: Sunny Lin
Editors: 
Last modified: Jul 9, 25

Functions to execute tasks and compute outputs for bot commands.
'''
from meeting import Meeting


# BOT FUNCTIONS:

def show(args: tuple[str], meetings: list[Meeting], now: float) -> str:
    '''
    Display the list of meetings in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of active meetings.

    Args can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings on record.
    - <label>: only display meetings of that label (multiple allowed).
    - <index>: only display meetings of that index (mutliple allowed).
    - -<all/label/index>: do not display meetings relevant to -args.

    Priority: index > label > all
    If a meeting has an arg label and another -arg label, it will still be displayed.

    Preconditions:
    - There cannot be a + and - arg with the same label/index.

    Sample Usage:
    >>> from constants import SAMPLE_MEETINGS, SAMPLE_NOW

    >>> show((), SAMPLE_MEETINGS, SAMPLE_NOW)
    '## 1. General Meeting 1 (soon)\\n<t:1749319200:F> (<t:300:R>)\\n## 3. Webmasters - Website\\n<t:1750190400:F> (<t:871500:R>)'
    
    >>> show(('full',), SAMPLE_MEETINGS, SAMPLE_NOW)
    "## 1. General Meeting 1 (soon)\\n<t:1749319200:F> (<t:300:R>)\\nOur first exec meeting of the year! Get to know each other and a run down on club operations.\\n**Participants:** <r>11111\\n## 3. Webmasters - Website\\n<t:1750190400:F> (<t:871500:R>)\\nGo over how we should begin coding the club's website.\\n**Participants:** <u>33333, <u>44444"

    >>> show(('all',), SAMPLE_MEETINGS, SAMPLE_NOW)
    '## 1. General Meeting 1 (soon)\\n<t:1749319200:F> (<t:300:R>)\\n## 2. Weekly Event Recap (weekly, paused)\\n<t:1749837600:F> (<t:518700:R>)\\n## 3. Webmasters - Website\\n<t:1750190400:F> (<t:871500:R>)\\n## 4. Tea Club Collab Meeting (canceled)\\n<t:1757606400:F> (<t:8287500:R>)'

    >>> show(('-all',), SAMPLE_MEETINGS, SAMPLE_NOW)
    ''

    >>> show(('-all', 'paused', 'canceled'), SAMPLE_MEETINGS, SAMPLE_NOW)
    '## 2. Weekly Event Recap (weekly, paused)\\n<t:1749837600:F> (<t:518700:R>)\\n## 4. Tea Club Collab Meeting (canceled)\\n<t:1757606400:F> (<t:8287500:R>)'

    >>> show(('-all', '3'), SAMPLE_MEETINGS, SAMPLE_NOW)
    '## 3. Webmasters - Website\\n<t:1750190400:F> (<t:871500:R>)'
    '''
    # print(meetings)

    # Turn all args lowercase.
    args = tuple(arg.lower() for arg in args)

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If current entry is not to be displayed, skip.
        if not curr_meeting.to_display(meetings_i, args): continue
        
        # Compute and add the output for the meeting.
        output += f'{curr_meeting.to_discord(
            meetings_i,
            now,
            'full' in args
        )}\n'
    
    # Return output, omitting the last \n.
    return output[:-1]


def add(meetings: list[Meeting], new_meeting: Meeting, by_date: bool = True) -> None:
    '''
    '''
    meetings.append(new_meeting)

    if by_date: meetings.sort(key=lambda m: m.get_time().get_timestamp())
    else: meetings.sort(key=lambda m: m.get_title())


if __name__ == '__main__':
    from doctest import testmod
    testmod()
