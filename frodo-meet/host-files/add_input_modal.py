'''Add Command Input Modal
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26
'''
from discord import ui, Interaction

from common_bot_helper import parse_input
from meeting import Meeting
from meeting_time import MeetingTime

LIST_INPUT_BREAKPOINT = ' '


class AddInputModal(ui.Modal, title='Add Meeting'):
    _title_input = ui.TextInput(label='Title')
    _time_input = ui.TextInput(label='Time')
    _description_input = ui.TextInput(label='Description', required=False)
    _participants_input = ui.TextInput(label='Participants', required=False)
    _labels_input = ui.TextInput(label='Labels', required=False)

    async def on_submit(self, interaction: Interaction):
        # If time input was invalid, print the error message.
        time = MeetingTime.from_input(self._time_input.value)
        if type(time) == str:
            await interaction.response.send_message(time)
            return

        meeting = Meeting(
            self._title_input.value,
            time,
            description = self._description_input.value,
            participants = parse_input(self._participants_input.value, LIST_INPUT_BREAKPOINT),
            labels = parse_input(self._labels_input.value, LIST_INPUT_BREAKPOINT),
        )

        await interaction.response.send_message(meeting.to_discord(is_full=True))
