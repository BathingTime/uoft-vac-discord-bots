'''Meeting class
Author: Sunny Lin
Editors: 
Last modified: Apr 6, 26
'''
from meeting_time import MeetingTime

LABELS = (
    'soon', # Happening in less than <NOTICE_TIME> seconds.
    'canceled', # Will not notify.
    'weekly', # Will be cloned same time next week upon beginning.
    'paused', # All subsequent meetings will not notify (for weekly meetings).
)


class Meeting:
    '''
    Contains all attributes of a meeting.

    Default init: args
    '''
    _title: str
    _time: MeetingTime
    _description: str
    _participants: list[str]
    _labels: list[str]

    def __init__(self,
        title: str,
        time: MeetingTime,
        description: str = '',
        participants: list[str] = [],
        labels: list[str] = [],
    ) -> None:
        self._title = title
        self._time = time
        self._description = description
        self._participants = participants
        self._labels = labels
    

    # INITS:

    @classmethod
    def from_file(cls, entry_data: dict):
        return cls(
            entry_data['title'],
            MeetingTime(entry_data['time']),
            entry_data['description'],
            entry_data['participants'],
            entry_data['labels'],
        )
    

    # INSTANCE METHODS:

    def to_discord(self, index: int | None = None, now: MeetingTime | None = None, is_full: bool = False) -> str:
        '''
        Return a string of the meeting's data be printed to Discord.

        Used by show command and data-modifying commands' input modals responses.

        Sample Usage:
        >>> from constants import SAMPLE_MEETINGS, SAMPLE_NOW

        >>> meeting = SAMPLE_MEETINGS[0]

        >>> meeting.to_discord()
        '## General Meeting 1 (soon)\\n<t:1749319200:F>'

        >>> meeting.to_discord(0)
        '## 1. General Meeting 1 (soon)\\n<t:1749319200:F>'

        >>> meeting.to_discord(0, SAMPLE_NOW)
        '## 1. General Meeting 1 (soon)\\n<t:1749319200:F> (<t:300:R>)'

        >>> meeting.to_discord(0, SAMPLE_NOW, True)
        '## 1. General Meeting 1 (soon)\\n<t:1749319200:F> (<t:300:R>)\\nOur first exec meeting of the year! Get to know each other and a run down on club operations.\\n**Participants:** <r>11111'
        '''
        time = self._time
        labels = self._labels

        output = '## '

        # If index given, add it.
        if index != None: output += f'{index + 1}. '

        # Add title.
        output += self._title

        # If meeting has any labels, add them in parentheses.
        if labels: output += f' ({', '.join(labels)})'
        
        # Add time on next line.
        output += f'\n{time.to_discord()}'

        # If current time given, add time difference.
        if now != None: output += \
            f' ({(time - now).to_discord(True)})'
        
        # If printing full, add description and unformatted participants on separate lines.
        if is_full: output += \
            f'\n{self._description \
            }\n**Participants:** {', '.join(self._participants)}'
        
        return output
    

    def to_display(self, index: int, args: tuple[str]) -> bool:
        ''''
        Given the meeting's index and args,
        returns if the meeting should be displayed.
        Specs are consistent with the show command's docstring.

        Used by show command.

        Sample Usage:
        >>> from sample_data import SAMPLE_MEETINGS

        >>> meeting = SAMPLE_MEETINGS[1]

        >>> meeting.to_display(0, ('all', 'weekly', '-1'))
        False

        >>> meeting.to_display(0, ('-all', '-weekly', '1'))
        True

        >>> meeting.to_display(0, ('-all', 'weekly', '-paused', '2'))
        True

        >>> meeting.to_display(0, ('all', '-paused', '2'))
        False

        >>> meeting.to_display(0, ('all', 'soon', '2'))
        True

        >>> meeting.to_display(0, ('-all', 'soon', '2'))
        False

        >>> meeting.to_display(0, ('soon', '2'))
        False
        '''
        # Refer to normal arguments (nonnegative arguments) as +arguments.

        index_inc = index + 1

        # If index is a -argument, do not display.
        if f'-{index_inc}' in args: return False
        
        # If index is a +argument, display.
        if f'{index_inc}' in args: return True
        
        labels = self._labels
        has_nlabel = False

        # Check labels.
        for label in labels:

            # If has a +argument label, display
            if label in args: return True
            
            # If has a -argument label, record it.
            if f'-{label}' in args: has_nlabel = True
        
        # If has no +argument label but has a -argument label, do not display.
        if has_nlabel: return False
        
        # If "all" is an argument, display.
        if 'all' in args: return True
        
        # If "-all" is an argument, do not display.
        if '-all' in args: return False
        
        # Displayed if it is active (has no canceled or paused label).
        return not ('canceled' in labels or 'paused' in labels)
    

    # Getters:
    def get_title(self) -> str: return self._title
    def get_time(self) -> MeetingTime: return self._time
    def get_description(self) -> str: return self._description
    def get_participants(self) -> list[str]: return self._participants
    def get_labels(self) -> list[str]: return self._labels

    # Setters:
    def set_title(self, title: str) -> None: self._title = title
    def set_time(self, time: MeetingTime) -> None: self._time = time
    def set_description(self, description: str) -> None: self._description = description
    def set_participants(self, participants: list[str]) -> None: self._participants = participants
    def set_labels(self, labels: list[str]) -> None: self._labels = labels

if __name__ == '__main__':
    from doctest import testmod
    testmod()
