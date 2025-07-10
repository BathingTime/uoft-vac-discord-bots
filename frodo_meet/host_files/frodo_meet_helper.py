'''Frodo Meet Helper
Author: Sunny Lin
Editor(s):
Last edited: Jul 6, 25

This file contains functions for computing outputs for frodo-meet.py.
'''
# Public packages:
from datetime import datetime

# Get the parent repo.
from sys import path as sys_path
from os import path as os_path

repo = os_path.abspath(os_path.join(__file__, *('..',) * 3))
sys_path.append(repo)

# Local Python files:
import common_bot_helper


# Constants:

# Tuple of stripped lines from meeting_entries_sample.txt.
# Use this in doctests.
SAMPLE_ENTRIES_LINES = common_bot_helper.get_file_lines('frodo_meet/meeting_entries_sample.txt')

NOTICE_TIME = 600 # Notify meetings that will begin in less than this value of seconds.

ENTRY_INFOS = (
    'title',
    'time',
    'details',
    'participants',
    'labels'
)

LABELS = ( # Constants for all labels; just rename these to change them.
    'SOON', # Happening in less than <NOTICE_TIME> seconds.
    'CANCELED', # Will not notify.
    'WEEKY', # Will be cloned same time next week upon beginning.
    'PAUSED' # All subsequent meetings will not notify (for weekly meetings).
)


# Helper functions:
def get_entries(lines: tuple[str]) -> list[dict]:
    '''Return a list of all meeting plan entries.
    Each entry should be a dict with keys as
    'title', 'time', 'details', 'participants', 'labels', each with their respective values.

    Sample Usage:
    >>> result = get_entries(SAMPLE_ENTRIES_LINES)
    >>> entry_1 = result[0]

    >>> entry_1['title']
    'General Meeting 1'

    >>> entry_1['time']
    [2025, 6, 7, 19, 0]

    >>> entry_1['details']
    'Our first exec meeting of the year! Get to know each other and a run down on club operations.'

    >>> entry_1['participants']
    ['everyone']

    >>> entry_1['labels']
    ['SOON']

    >>> entry_2 = result[1]

    >>> entry_2['title']
    'Weekly Event Recap'

    >>> entry_2['time']
    [2025, 6, 13, 19, 0]

    >>> entry_2['details']
    "Go over today's event. How did it go, anything nice, any improvements for the future, etc."

    >>> entry_2['participants']
    ['<r>11111']

    >>> entry_2['labels']
    ['WEEKLY', 'PAUSED']
    '''
    # Make an empty list to be returned.
    output = []

    # Begin with the first line.
    pos_lines = 0

    # Initialise the entry dict.
    curr_entry = {}

    # Distinguish each piece of info in an entry with an index (1–5).
    info_i = 1

    # Keep reading the file until there are no lines left.
    lines_count = len(lines)
    while pos_lines < lines_count:

        # Get the current line.
        curr_line = lines[pos_lines]

        # Separate the key and value of the current line.
        pos_colon = curr_line.find(':')
        key, val = curr_line[:pos_colon], curr_line[pos_colon + 2:]
        
        # If the current piece of info is date, participants, or labels,
        # turn the value into a list by splitting it at spaces.
        if info_i in (2, 4, 5):
            val = val.split()

            # If the current piece of info is date,
            # typecast all individual values into ints as well.
            if info_i == 2:
                val = [int(num) for num in val]
        
        # Insert the key-value pair into the entry dict.
        curr_entry[key] = val

        # If the current piece of info is not the last one, advance.
        if info_i != len(ENTRY_INFOS):
            info_i += 1
        
        # Otherwise, the entry has been completely read.
        else:

            # Reset the info index.
            info_i = 1

            # Add the entry dict to the output list and reset the dict.
            output.append(curr_entry)
            curr_entry = {}

            # Advance to the next line ahead of time, which should be empty.
            pos_lines += 1

        # Advance to the next line.
        pos_lines += 1
    
    # Return.
    return output

def get_now() -> tuple[int, int, int, int, int]:
    '''Return the current time in the following format:
    (year, month, day, hour, minute)

    Sample usage does not reflect the complete reliability of the function since
    datetime.now() would output different times every time.

    Sample Usage:
    >>> now = get_now()

    >>> len(now) == 5
    True

    >>> all(type(val) == int for val in now)
    True

    >>> 1 <= now[1] <= 12
    True

    >>> 0 <= now[3] <= 23
    True

    >>> 0 <= now[4] <= 59
    True
    '''
    now = str(datetime.now())

    return tuple(int(val) for val in (
        now[0:4], # year
        now[5:7], # month
        now[8:10], # day
        now[11:13], # hour
        now[14:16] # minute
        ))

def to_display(args: tuple[str], labels: list[str], index: int) -> bool:
    ''''Returns if a meeting plan should be displayed according to the arguments.

    Sample Usage:
    >>> to_display(('ALL', 'WEEKLY', '-1'), ['WEEKLY', 'PAUSED'], 0)
    False

    >>> to_display(('-ALL', '-PAUSED', '1'), ['WEEKLY', 'PAUSED'], 0)
    True

    >>> to_display(('-ALL', 'WEEKLY', '-PAUSED', '2'), ['WEEKLY', 'PAUSED'], 0)
    True

    >>> to_display(('ALL', '-PAUSED', '2'), ['WEEKLY', 'PAUSED'], 0)
    False

    >>> to_display(('ALL', 'SOON', '2'), ['WEEKLY', 'PAUSED'], 0)
    True

    >>> to_display(('-ALL', 'SOON', '2'), ['WEEKLY', 'PAUSED'], 0)
    False

    >>> to_display(('SOON', '2'), ['WEEKLY', 'PAUSED'], 0)
    False

    >>> to_display(('SOON', '2'), ['WEEKLY'], 0)
    True
    '''
    # If the entry's index is a -argument, it won't be displayed.
    if '-' + str(index + 1) in args:
        return False
    
    # Else if the entry's index is an argument, it will be displayed.
    if str(index + 1) in args:
        return True
    
    has_nlabel = False

    # Else if the entry has an argument label, it will be displayed.
    for label in labels:
        if label in args:
            return True
        
        # If the entry has a -argument label, record it.
        if '-' + label in args:
            has_nlabel = True
    
    # Else if the entry has no argument label but has a -argument label,
    # it won't be displayed.
    if has_nlabel:
        return False
    
    # Else if "all" is an argument, it will be displayed.
    if 'ALL' in args:
        return True
    
    # Else if "-all" is an argument, it will not be displayed.
    if '-ALL' in args:
        return False
    
    # Else, it will be displayed if it is active (has no CANCELED or PAUSED label).
    return not (LABELS[1] in labels or LABELS[3] in labels)


# Bot command functions:
def show(args: tuple[str], entries:list[dict], now: tuple[int]) -> tuple[bool, str]:
    '''Display the list of meeting plans in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of all active meeting plans.

    Arguments can be passed for more options:
    - full: also display details, participants.
    - all: display all meeting plans on record.
    - <label>: only display meeting plans of that label (multiple allowed).
    - <index>: only display meeting plans of that index (mutliple allowed).
    - -<all/label/index>: do not display meeting plans relevant to -arguments.

    Priority: index -> label -> all
    If an entry has an argument label and another -argument label, it will still be displayed.

    Preconditions:
    - There cannot be a + and - argument with the same label/index.

    Sample Usage:
    >>> sample_entries = get_entries(SAMPLE_ENTRIES_LINES)

    >>> show((), sample_entries, (2025, 6, 7, 18, 55))
    '# 1. General Meeting 1 (SOON)\\n**2025-06-07 19:00:00 (0:05:00 left)**\\n\\n# 3. Webmasters 2 - Website\\n**2025-06-17 20:00:00 (10 days, 1:05:00 left)**'

    >>> show(('full',), sample_entries, (2025, 6, 7, 18, 55))
    "# 1. General Meeting 1 (SOON)\\n**2025-06-07 19:00:00 (0:05:00 left)**\\nOur first exec meeting of the year! Get to know each other and a run down on club operations.\\n**Participants:** everyone\\n\\n# 3. Webmasters 2 - Website\\n**2025-06-17 20:00:00 (10 days, 1:05:00 left)**\\nGo over how we should begin coding the club's website.\\n**Participants:** <u>22222, <u>33333"

    >>> show(('all',), sample_entries, (2025, 6, 7, 18, 55))
    '# 1. General Meeting 1 (SOON)\\n**2025-06-07 19:00:00 (0:05:00 left)**\\n\\n# 2. Weekly Event Recap (WEEKLY, PAUSED)\\n**2025-06-13 19:00:00 (6 days, 0:05:00 left)**\\n\\n# 3. Webmasters 2 - Website\\n**2025-06-17 20:00:00 (10 days, 1:05:00 left)**\\n\\n# 4. Tea Club Collab Meeting (CANCELED)\\n**2025-09-11 16:00:00 (95 days, 21:05:00 left)**'

    >>> show(('-all',), sample_entries, (2025, 6, 7, 18, 55))
    ''

    >>> show(('-all', 'paused', 'canceled'), sample_entries, (2025, 6, 7, 18, 55))
    '# 2. Weekly Event Recap (WEEKLY, PAUSED)\\n**2025-06-13 19:00:00 (6 days, 0:05:00 left)**\\n\\n# 4. Tea Club Collab Meeting (CANCELED)\\n**2025-09-11 16:00:00 (95 days, 21:05:00 left)**'

    >>> show(('-all', '3'), sample_entries, (2025, 6, 7, 18, 55))
    '# 3. Webmasters 2 - Website\\n**2025-06-17 20:00:00 (10 days, 1:05:00 left)**'
    '''
    # Turn all arguments lowercase.
    args = tuple(arg.upper() for arg in args)

    # Initialise a list of strings for each entry to be outputted.
    output_strings = []

    # Iterate through all meeting plan entries.
    for pos_entries in range(len(entries)):

        # Get the current entry.
        curr_entry = entries[pos_entries]

        meeting_labels = curr_entry['labels']

        # If the current entry is not to be displayed, skip.
        if not to_display(args, meeting_labels, pos_entries):
            continue

        # Get the datetime object for the meeting's time.
        meeting_time = datetime(*curr_entry['time'])

        # Add the entry index & meeting title first.
        output_string = '# ' + str(pos_entries + 1) + '. ' + curr_entry['title']

        # If the meeting has any labels, add them in parentheses.
        if meeting_labels:
            output_string += ' (' + ', '.join(meeting_labels) + ')'
        
        # Then, add the meeting time & time difference on the next line.
        output_string += '\n**' + str(meeting_time) + ' (' + str(meeting_time - datetime(*now)) + ' left)**'
        
        # If "full" is an argument, add the entry details & unformatted participants on separate lines.
        if 'FULL' in args:
            output_string += '\n' + curr_entry['details'] + '\n' + \
                '**Participants:** ' + ', '.join(curr_entry['participants'])
        
        # Add the string to the output list.
        output_strings.append(output_string)
    
    # Return the single string version with each string separated by an empty line.
    return '\n\n'.join(output_strings)

def add(args: tuple[str], entries: list[dict]) -> str:
    '''
    '''

def cancel(args: tuple[str], entries: list[dict]) -> str:
    '''
    '''

def edit(args: tuple[str], entries: list[dict]) -> str:
    '''
    '''


if __name__ == '__main__':
    from doctest import testmod
    testmod()
