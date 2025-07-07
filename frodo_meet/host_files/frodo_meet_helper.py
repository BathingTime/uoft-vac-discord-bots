'''Frodo Meet Helper
Author: Sunny Lin
Editor(s):
Last edited: Jul 6, 25

This file contains functions for computing outputs for frodo-meet.py.
'''
from datetime import datetime


# Constants:
ENTRY_INFOS = 5 # Number of pieces of info each meeting plan entry should have.

# Helper functions:
def read_file(file_path: str) -> list[dict[str, str, str, tuple[str]]]:
    '''Return a tuple of all meeting plan entries.
    Each entry should be a dict with keys as
    'Date', 'Title', 'Details', 'Participants', each with their respective values.

    Sample usage inapplicable.
    '''
    # Make an empty list to be returned.
    output = []

    # Open the file to read.
    with open(file_path, 'r') as file_read:

        # Begin with the first line.
        curr_line = file_read.readline().strip()

        # Initialise the entry dict.
        curr_entry = {}

        # Distinguish each piece of info in an entry with an index (1–5).
        info_i = 1

        # Keep reading the file until there are no lines left.
        while curr_line:

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
            if info_i != ENTRY_INFOS:
                info_i += 1
            
            # Otherwise, the entry has been completely read.
            else:

                # Reset the info index.
                info_i = 1

                # Add the entry dict to the output list and reset the dict.
                output.append(curr_entry)
                curr_entry = {}

                # Advance to the next line ahead of time, which should be empty.
                file_read.readline()

            # Advance to the next line.
            curr_line = file_read.readline().strip()
    
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


# Bot command functions:
def show(args: tuple[str], entries:list[dict], now: tuple[int]) -> str:
    '''Display the list of meeting plans.
    '''

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
