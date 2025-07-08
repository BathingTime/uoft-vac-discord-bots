'''Frodo Meet Helper
Author: Sunny Lin
Editor(s):
Last edited: Jul 6, 25

This file contains functions for computing outputs for frodo-meet.py.
'''
from datetime import datetime


# Constants:
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

    >>> result = get_entries((
    ... "title: General Meeting 1",
    ... "time: 2025 06 07 19 00",
    ... "details: Our first exec meeting…",
    ... "participants: @everyone",
    ... "labels: SOON",
    ... "",
    ... "title: Weekly Event Recap",
    ... "time: 2025 06 13 19 00",
    ... "details: Go over today's event…",
    ... "participants: &11111",
    ... "labels: WEEKLY PAUSED",
    ... ""
    ... ))

    >>> result[0]['title']
    'General Meeting 1'

    >>> result[0]['time']
    [2025, 6, 7, 19, 0]

    >>> result[0]['details']
    'Our first exec meeting…'

    >>> result[0]['participants']
    ['@everyone']

    >>> result[0]['labels']
    ['SOON']

    >>> result[1]['title']
    'Weekly Event Recap'

    >>> result[1]['time']
    [2025, 6, 13, 19, 0]

    >>> result[1]['details']
    "Go over today's event…"

    >>> result[1]['participants']
    ['&11111']

    >>> result[1]['labels']
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
    >>> to_display(('all', 'WEEKLY', '-1'), ['WEEKLY', 'PAUSED'], 1)
    False

    >>> to_display(('-all', '-PAUSED', '1'), ['WEEKLY', 'PAUSED'], 1)
    True

    >>> to_display(('-all', 'WEEKLY', '-PAUSED', '2'), ['WEEKLY', 'PAUSED'], 1)
    True

    >>> to_display(('all', '-PAUSED', '2'), ['WEEKLY', 'PAUSED'], 1)
    False

    >>> to_display(('all', 'SOON', '2'), ['WEEKLY', 'PAUSED'], 1)
    True

    >>> to_display(('-all', 'SOON', '2'), ['WEEKLY', 'PAUSED'], 1)
    False

    >>> to_display(('SOON', '2'), ['WEEKLY', 'PAUSED'], 1)
    False

    >>> to_display(('SOON', '2'), ['WEEKLY'], 1)
    True
    '''
    # If the entry's index is a -argument, it won't be displayed.
    if '-' + str(index) in args:
        return False
    
    # Else if the entry's index is an argument, it will be displayed.
    if str(index) in args:
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
    if 'all' in args:
        return True
    
    # Else if "-all" is an argument, it will not be displayed.
    if '-all' in args:
        return False
    
    # Else, it will be displayed if it is active (has no CANCELED or PAUSED label).
    return not (LABELS[2] in labels or LABELS[4] in labels)


# Bot command functions:
def show(args: tuple[str], entries:list[dict], now: datetime) -> tuple[bool, str]:
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
    >>> sample_entries = [
    ... {
    ... 'title': "General Meeting 1",
    ... 'time': [2025, 6, 7, 19, 0],
    ... 'details': "Our first exec meeting…",
    ... 'participants': ['@everyone'],
    ... 'labels': ['SOON']
    ... },
    ... {
    ... 'title': "Weekly Event Recap",
    ... 'time': [2025, 6, 13, 19, 0],
    ... 'details': "Go over today's event…",
    ... 'participants': ['&11111'],
    ... 'labels': ['WEEKLY', 'PAUSED']
    ... },
    ... {
    ... 'title': "Webmasters 2 - Website",
    ... 'time': [2025, 6, 17, 20, 0],
    ... 'details': "Go over how we should…",
    ... 'participants': ['22222', '33333'],
    ... 'labels': []
    ... }
    ... ]

    # >>> show((), sample_entries, (2025, 6, 7, 18, 55))
    '''
    # Turn all arguments lowercase.
    args = tuple(arg.upper() for arg in args)

    # Initialise a list of strings for each entry to be outputted.
    output_strings = []

    # Iterate through all meeting plan entries.
    for pos_entries in range(len(entries)):

        # Get the current entry.
        curr_entry = entries[pos_entries]

        meeting_labels = curr_entry[4]

        # If the current entry is not to be displayed, skip.
        if not to_display(args, meeting_labels, pos_entries):
            continue

        # Get the datetime object for the meeting's time.
        meeting_time = datetime(*curr_entry[1])

        # Add the entry's index, title, labels, time, & time difference to the output.
        output_string = '# ' + str(pos_entries) + '. ' + curr_entry[0] + '(' + ', '.join(meeting_labels) + ')\n' + \
            '**' + str(meeting_time) + '(' + str(meeting_time - now) + ' left)**' + '\n'
        
        # If "full" is an argument, add the entry's details & participants' display names as well.
        if 'full' in args:
            output_string += curr_entry[2] + '\n' + '**Participants:** ' + ...
        
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
