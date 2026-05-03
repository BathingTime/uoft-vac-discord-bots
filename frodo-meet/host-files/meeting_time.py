'''Frodo Meet - MeetingTime Class
'''
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from common_bot_helper import parse_input

TORONTO_TIMEZONE = ZoneInfo("America/Toronto")


class MeetingTime:
    '''
    Stores all relevant args for a meeting time,
    as well as its UNIX timestamp equivalent.

    Default init: timestamp
    '''
    _timestamp: float

    def __init__(self, timestamp: float) -> None:
        self._timestamp = timestamp
    
    @classmethod
    def get_now(cls) -> MeetingTime: return cls(datetime.now(TORONTO_TIMEZONE))


    # INSTANCE METHODS

    def to_discord(self, relative: bool = False) -> str:
        return f'<t:{int(self.get_timestamp())}:{'F' if not relative else 'R'}>'


    def is_within_timeframe(self, other: MeetingTime | int, timeframe_secs: int) -> bool:
        return (self - other).get_timestamp() <= timeframe_secs


    # OPERATIONS

    def __add__(self, other: MeetingTime | int) -> MeetingTime:
        if isinstance(other, MeetingTime):
            return MeetingTime(self.get_timestamp() + other.get_timestamp())
        
        if isinstance(other, int):
            return MeetingTime(self.get_timestamp() + other)
        
        return NotImplemented

    def __sub__(self, other: MeetingTime | int) -> MeetingTime:
        return self + (-other)

    def __neg__(self) -> MeetingTime:
        return MeetingTime(-self.get_timestamp())


    def get_timestamp(self) -> float: return self._timestamp


    # FROM INPUT

    @classmethod
    def from_input(cls, input: str) -> MeetingTime | str:
        args = parse_input(input, TIME_BREAKPOINTS_RE) # Args are lowercase.
        num_args = len(args)

        # If invalid number of args, terminate.
        if not 1 <= num_args <= 5:
            return build_err_message(['Number of arguments must be **1–5**.'])

        now = datetime.now(TORONTO_TIMEZONE)
        err_specs = []


        # 5 args: Y Mon D H Min
        if num_args == 5:
            try:
                try:
                    year = int(args[0])
                    day = int(args[2])
                    hour = int(args[3])
                    minute = int(args[4])
                except ValueError: raise ValueError(INVALID_NUM)

                month = get_month_int(args[1])
                if not month: raise ValueError(INVALID_MON)

                if not 0 <= hour < 24: raise ValueError(INVALID_H)
                if not 0 <= minute < 60: raise ValueError(INVALID_MIN)

                try: dt = datetime(
                    year, month, day, hour, minute,
                    tzinfo = TORONTO_TIMEZONE
                )
                except ValueError: raise ValueError(INVALID_DT)

                if dt <= now: raise ValueError(INVALID_PASSED)

                return cls(dt.timestamp())

            except ValueError as e: add_err_spec(err_specs, 'Y Mon D H Min', e)


        # 4 args: Mon D H Min
        if num_args == 4:
            try:
                try:
                    day = int(args[1])
                    hour = int(args[2])
                    minute = int(args[3])
                except ValueError: raise ValueError(INVALID_NUM)

                month = get_month_int(args[0])
                if not month: raise ValueError(INVALID_MON)

                if not 0 <= hour < 24: raise ValueError(INVALID_H)
                if not 0 <= minute < 60: raise ValueError(INVALID_MIN)

                year = now.year

                try: dt = datetime(
                    year, month, day, hour, minute,
                    tzinfo = TORONTO_TIMEZONE
                )
                except ValueError: raise ValueError(INVALID_DT)

                if dt <= now: dt = datetime(
                    year + 1, month, day, hour, minute,
                    tzinfo = TORONTO_TIMEZONE
                )

                return cls(dt.timestamp())

            except ValueError as e: add_err_spec(err_specs, 'Mon D H Min', e)


        # 3 args:
        # Case 1: Y Mon D
        # Case 2: W H Min
        if num_args == 3:

            # Try Case 1.
            try:
                try:
                    year = int(args[0])
                    day = int(args[2])
                except ValueError: raise ValueError(INVALID_NUM)

                month = get_month_int(args[1])
                if not month: raise ValueError(INVALID_MON)

                try: dt = datetime(
                    year, month, day,
                    DEFAULT_HOUR, DEFAULT_MINUTE,
                    tzinfo = TORONTO_TIMEZONE
                )
                except ValueError: raise ValueError(INVALID_DT)

                if dt <= now: raise ValueError(INVALID_PASSED)

                return cls(dt.timestamp())

            except ValueError as e: add_err_spec(err_specs, 'Y Mon D', e)

            # If case 1 failed, try case 2.
            try:
                try:
                    hour = int(args[1])
                    minute = int(args[2])
                except ValueError: raise ValueError(INVALID_NUM)

                if not 0 <= hour < 24: raise ValueError(INVALID_H)
                if not 0 <= minute < 60: raise ValueError(INVALID_MIN)

                weekday = WEEKDAY_MAP.get(args[0])
                if weekday is None: raise ValueError(INVALID_W)

                return cls(
                    next_weekday(now, weekday, hour, minute)
                    .timestamp()
                )

            except ValueError as e: add_err_spec(err_specs, 'W H Min', e)


        # 2 args:
        # Case 1: Mon D
        # Case 2: H Min
        if num_args == 2:

            # Try case 1.
            try:
                try: day = int(args[1])
                except ValueError: raise ValueError(INVALID_NUM)

                month = get_month_int(args[0])
                if not month: raise ValueError(INVALID_MON)

                year = now.year

                try: dt = datetime(
                    year, month, day,
                    DEFAULT_HOUR, DEFAULT_MINUTE,
                    tzinfo=TORONTO_TIMEZONE
                )
                except ValueError: raise ValueError(INVALID_DT)

                if dt <= now: dt = datetime(
                    year + 1, month, day,
                    DEFAULT_HOUR, DEFAULT_MINUTE,
                    tzinfo = TORONTO_TIMEZONE
                )

                return cls(dt.timestamp())

            except ValueError as e: add_err_spec(err_specs, 'Mon D', e)

            # If case 1 failed, try case 2.
            try:
                try:
                    hour = int(args[0])
                    minute = int(args[1])
                except ValueError: raise ValueError(INVALID_NUM)

                if not 0 <= hour < 24: raise ValueError(INVALID_H)
                if not 0 <= minute < 60: raise ValueError(INVALID_MIN)

                dt = now.replace(
                    hour = hour,
                    minute = minute,
                    second = 0,
                    microsecond=0
                )

                if dt <= now: dt += timedelta(days=1)

                return cls(dt.timestamp())

            except ValueError as e: add_err_spec(err_specs, 'H Min', e)


        # 1 arg: W
        if num_args == 1:
            try:
                weekday = WEEKDAY_MAP.get(args[0])
                if weekday is None: raise ValueError(INVALID_W)

                return cls(
                    next_weekday(
                        now, weekday,
                        DEFAULT_HOUR, DEFAULT_MINUTE
                    )
                    .timestamp()
                )

            except ValueError as e: add_err_spec(err_specs, 'W', e)


        return build_err_message(err_specs)


# CONSTANTS & HELPER FUNCTIONS for from_input.

MONTH_MAP = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}
WEEKDAY_MAP = {
    'monday': 0, 'mon': 0,
    'tuesday': 1, 'tues': 1, 'tue': 1,
    'wednesday': 2, 'wed': 2,
    'thursday': 3, 'thurs': 3, 'thu': 3,
    'friday': 4, 'fri': 4,
    'saturday': 5, 'sat': 5,
    'sunday': 6, 'sun': 6
}

DEFAULT_HOUR = 18 # 6pm
DEFAULT_MINUTE = 0

TIME_BREAKPOINTS_RE = '[ ,:-]'

INVALID_NUM = 'Expected numeric arguments(s) not numeric.'
INVALID_MON = 'Invalid month.'
INVALID_H = 'Hour must be 0–24, not including 24.'
INVALID_MIN = 'Minute must be 0–60, not including 60.'
INVALID_W = 'Invalid weekday.'
INVALID_DT = 'Call to datetime failed.'
INVALID_PASSED = 'Intended time has already passed.'


def get_month_int(arg: str) -> int:
    if arg.isdigit():
        arg = int(arg)
        
        return arg if 1 <= arg <= 12 else None
    
    return MONTH_MAP.get(arg)
    # If invalid, will return None.

def next_weekday(
    now: datetime,
    target_weekday: int,
    hour: int,
    minute: int
) -> datetime:
    days_ahead = (target_weekday - now.weekday()) % 7

    if days_ahead == 0:
        candidate = now.replace(
            hour = hour,
            minute = minute,
            second = 0,
            microsecond = 0
        )

        if candidate > now:
            return candidate
        
        days_ahead = 7
    
    return (now + timedelta(days=days_ahead)).replace(
        hour = hour,
        minute = minute,
        second = 0,
        microsecond = 0
    )

def add_err_spec(err_specs: list[str], format: str, err: str) -> None:
    err_specs.append(f'**{format}** format failed: __{err}__')

def build_err_message(err_specs: list[str]) -> str:
    return (
        'Invalid time input. 🧐\n'
        f'{'\n'.join(err_specs)}\n\n'
        'Refer to the input specifications for time input with the **help** command.'
    )


if __name__ == '__main__':
    from doctest import testmod
    testmod()
