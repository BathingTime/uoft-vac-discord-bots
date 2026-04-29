'''Frodo Meet - Auto Functions
'''
from frodo_meet_helper import add_meeting

from meeting import Meeting,\
    SOON_LABEL,\
    NON_NOTIFY_LABELS,\
    NON_BEGIN_LABELS,\
    RECURRING_LABELS
from meeting_time import MeetingTime


def notify_meetings(meetings: list[Meeting], now: MeetingTime, notice_time_secs: int) -> str:
    '''
    Check if any active meetings not marked as 'soon' is within the notice time.
    Return a string of notify messages for all meetings that this applies to,
    and mark these meetings as 'soon' if they haven't been already.
    Return None if there are no meetings to notify.

    Preconditions:
    - meetings are sorted by timestamp.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS, EPOCH

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> m0, m2, m3 = meetings[0], meetings[2], meetings[3]
    >>> m0.has_labels(SOON_LABEL) or m2.has_labels(SOON_LABEL) or m3.has_labels(SOON_LABEL)
    []

    >>> notify_meetings(meetings, EPOCH, 10)
    '**past** will begin soon!\\n## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: <@&12345>'

    >>> m0.has_labels(SOON_LABEL) and m2.has_labels(SOON_LABEL)
    ['soon']

    >>> notify_meetings(meetings, EPOCH, 20)
    '**no description** will begin soon!\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐'

    >>> m3.has_labels(SOON_LABEL)
    ['soon']

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> notify_meetings(meetings, EPOCH, 20)
    'The following meetings will begin soon!\\n## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: <@&12345>\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐'
    '''
    output_list = []

    # Check all meetings.
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If meeting is not within the notice time,
        # no subsequent meetings can be since they are sorted, so stop checking.
        if not curr_meeting.is_soon(now, notice_time_secs): break

        # If meeting has any non-notify labels, skip.
        if curr_meeting.has_labels(*NON_NOTIFY_LABELS):
            # Mark meeting as soon if applicable.
            curr_meeting.add_label(SOON_LABEL)
            continue

        # Otherwise, add it to the output.

        # If it's the first meeting to notify, record it in case it's the only one.
        if not output_list: first_meeting = curr_meeting

        # Add meeting to notify.
        output_list.append(curr_meeting.to_discord(index=meetings_i, full=True))

        # Mark meeting as soon.
        curr_meeting.add_label(SOON_LABEL)
    
    num_outputs = len(output_list)

    # If there are meetings to notify, return output.
    if num_outputs > 1: return f'The following meetings will begin soon!\n{'\n'.join(output_list)}'
    if num_outputs == 1: return f'{first_meeting.get_title(True)} will begin soon!\n{output_list[0]}'
    
    # Otherwise, there are no meetings to notify, so don't print anything.
    return None


def begin_meetings(meetings: list[Meeting], now: MeetingTime) -> str:
    '''
    Return a string of begin messages for all active meetings that have begun.
    For such meetings, remove regular meetings for the meetings list, and
    clone recurring meetings with the appropriate time increment.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS, EPOCH

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> begin_meetings(meetings, EPOCH)
    '**past** has started! Happy meeting! 🎈\\n**past, has soon, daily, multiple participants** has started and was cloned same time tomorrow! Happy meeting! 🎈\\n'

    >>> [meeting.get_title() for meeting in meetings]
    ['soon, canceled', 'no description', 'not soon', 'past, has soon, daily, multiple participants', 'past, weekly, paused, no participants']

    >>> meetings[3].get_time().get_timestamp()
    86400.0

    >>> meetings[4].get_time().get_timestamp()
    604800.0

    >>> meetings[3].get_time().get_timestamp() == RECURRING_LABELS['daily'][0]
    True

    >>> meetings[4].get_time().get_timestamp() == RECURRING_LABELS['weekly'][0]
    True
    '''
    output = ''

    # Check meetings until they're not past.
    while meetings and meetings[0].is_past(now):

        # Pop the current meeting from the meetings list.
        curr_meeting = meetings.pop(0)

        # If meeting is recurring, clone it with the appropriate time increment.
        recurring_label = curr_meeting.has_labels(*RECURRING_LABELS.keys())
        if recurring_label:
            recurring_label_result = RECURRING_LABELS[recurring_label[0]]

            clone = Meeting.clone(curr_meeting, recurring_label_result[0])
            clone.remove_label(SOON_LABEL) # Remove soon label if applicable (likely).
            add_meeting(meetings, clone)

            recurring_output = f' and was cloned same time {recurring_label_result[1]}'
        
        else: recurring_output = ''
        
        # If meeting is active, add it to begin.
        if not curr_meeting.has_labels(*NON_BEGIN_LABELS):
            output += f'{curr_meeting.get_title(True)} has started{recurring_output}! Happy meeting! 🎈\n'
    
    return output if output else None


if __name__ == '__main__':
    from doctest import testmod
    testmod()
