'''Frodo Meet - Edit Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from copy import deepcopy

from common.util import (
    get_response,
    parse_input,
    ConfirmationViewDefault,
    RESPONSE_TIMEOUT,
    NULL_SELECT_VALUE,
)

from frodo_meet_helper import (
    get_meetings_to_discord,
    find_meeting,
    add_meeting,
    remove_meeting,
    is_title_taken,
    verify_names,
    get_ping_str,
    dm_meeting,
    build_failed_dm_err,
)
from frodo_meet_discord_views import MeetingSelectView, RecurrenceSelectView
from frodo_meet_data import save_meetings
from meeting import (Meeting,
    ATTRIBUTE_TITLE,
    ATTRIBUTE_TIME,
    ATTRIBUTE_DESCRIPTION,
    ATTRIBUTE_PARTICIPANTS,
    ATTRIBUTE_DM,
    ATTRIBUTE_RECURRENCE,
    PARTICIPANTS_BREAKPOINTS,
)
from meeting_time import MeetingTime

PARTICIPANTS_ADD = 'Add Participants'
PARTICIPANTS_REMOVE = 'Remove Participants'
DM_ADD = 'Add pings by DM'
DM_REMOVE = 'Remove pings by DM'


async def edit_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    names_to_pings: dict[str: str],
    target: str
) -> None:
    print('Edit meeting command start.')

    if not meetings:
        await interaction.response.send_message('There are no meetings to edit. 🧐')
        print('No meetings, terminating.')
        return
    
    # STEP 1: If no target arg was given, go to meeting select.
    if not target:
        print('No target string, sending meeting select view.')

        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting you want to delete:\n'
                f'{get_meetings_to_discord(meetings, ('all',))}'
            ),
            view = MeetingSelectView(
                on_meeting_select,
                meetings,
                names_to_pings = names_to_pings
            )
        )
        return
    
    # Get target meeting.
    print('Have target string, finding target meeting.')

    target_meeting = find_meeting(meetings, target)
    if isinstance(target_meeting, str):
        await interaction.response.send_message(target_meeting)
        print('Find meeting error, terminating.')
        return
    
    # STEP 2: Get property to edit.
    print('Got target meeting, sending edit property select view.')

    await interaction.response.send_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, target_meeting, names_to_pings)
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    names_to_pings: dict[str: str]
) -> None:
    # STEP 2: Get property to edit.
    print('In on meeting select, sending edit property select view.')

    await interaction.response.edit_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, target_meeting, names_to_pings)
    )

def build_on_meeting_select_content(target_meeting: Meeting) -> str:
    return (
        f'You are editing {target_meeting.get_title(True)}.\n'
        'Which property would you like to edit?'
    )


# EDIT PROPERTY SELECT

class EditPropertySelectView(View):
    def __init__(self,
        meetings: list[Meeting],
        target_meeting: Meeting,
        names_to_pings: dict[str: str]
    ) -> None:
        print('In edit property select view, awaiting target property select…')
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(EditPropertySelect(meetings, target_meeting, names_to_pings))

class EditPropertySelect(Select):
    _meetings: list[Meeting]
    _target_meeting: Meeting
    _names_to_pings: dict[str: str]

    def __init__(self,
        meetings: list[Meeting],
        target_meeting: Meeting,
        names_to_pings: dict[str: str]
    ) -> None:
        self._meetings = meetings
        self._target_meeting = target_meeting
        self._names_to_pings = names_to_pings

        super().__init__(
            placeholder = 'Select property…',
            options = [
                SelectOption(label = ATTRIBUTE_TITLE.capitalize(), value = ATTRIBUTE_TITLE),
                SelectOption(label = ATTRIBUTE_TIME.capitalize(), value = ATTRIBUTE_TIME),
                SelectOption(label = ATTRIBUTE_DESCRIPTION.capitalize(), value = ATTRIBUTE_DESCRIPTION),
                SelectOption(label = PARTICIPANTS_ADD, value = PARTICIPANTS_ADD),
                SelectOption(label = PARTICIPANTS_REMOVE, value = PARTICIPANTS_REMOVE),
                SelectOption(label = DM_ADD, value = DM_ADD),
                SelectOption(label = DM_REMOVE, value = DM_REMOVE),
                SelectOption(label = ATTRIBUTE_RECURRENCE.capitalize(), value = ATTRIBUTE_RECURRENCE),
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        print('Target property selected.')
        target_property = self.values[0]

        meetings = self._meetings
        names_to_pings = self._names_to_pings
        target_meeting = self._target_meeting

        # Deepcopy target meeting for preview of changes.
        updated_meeting = deepcopy(target_meeting)

        # STEP 3: Get new value.
        # If editing recurrence, go to recurrence select view.
        if target_property == ATTRIBUTE_RECURRENCE:
            print('Editing recurrence, sending recurrence select view.')

            await interaction.response.edit_message(
                content = (
                    f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                    'Please select the new recurrence.\n'
                    'For a one-time meeting, select *Normal (one-time)*.'
                ),
                view = RecurrenceSelectView(
                    on_select = on_recurrence_select,
                    meetings = meetings,
                    target_meeting = target_meeting,
                    updated_meeting = updated_meeting,
                    names_to_pings = names_to_pings,
                    target_property = target_property
                )
            )
            return

        # Otherwise, await new value as a response.
        print('Awaiting new value…')

        await interaction.response.edit_message(
            content = (
                f'You are editing the __{build_target_property_content(target_property)}__ of {target_meeting.get_title(True)}.\n'
                'Please enter the new value *as you would when creating a new meeting*.'
            ),
            view = None
        )
        
        new_value_input = await get_response(interaction)
        print('Got new value.')

        new_names = []

        # If editing title:
        if target_property == ATTRIBUTE_TITLE:
            print('Editing title.')

            title = new_value_input.content
            taken_err = is_title_taken(meetings, title)

            # If title is taken, send error message and terminate.
            if taken_err:
                await interaction.followup.send(taken_err)
                print('Title taken error, terminating.')
                return
            
            updated_meeting.set_title(title)

        # If editing time:
        elif target_property == ATTRIBUTE_TIME:
            print('Editing time.')

            time = MeetingTime.from_input(new_value_input.content)

            if isinstance(time, str):
                await interaction.followup.send(time)
                print('Time error, terminating.')
                return
            
            updated_meeting.set_time(time)

            # Reset meeting's soon status.
            updated_meeting.set_soon()
        
        # If editing description:
        elif target_property == ATTRIBUTE_DESCRIPTION:
            print('Editing description.')
            updated_meeting.set_description(new_value_input.content)
        
        # If adding participants:
        elif target_property == PARTICIPANTS_ADD:
            print('Adding participants.')
            new_names = verify_names(
                parse_input(new_value_input.content, PARTICIPANTS_BREAKPOINTS),
                self._names_to_pings
            )
            print(f'After verify: {new_names}')
            updated_meeting.add_names(new_names, ATTRIBUTE_PARTICIPANTS)
            print(f'After update: {new_names}')
        
        # If removing participants:
        elif target_property == PARTICIPANTS_REMOVE:
            print('Removing participants.')
            new_names = parse_input(
                new_value_input.content, PARTICIPANTS_BREAKPOINTS
            )
            updated_meeting.remove_names(new_names, ATTRIBUTE_PARTICIPANTS)
        
        # If adding pings by dm:
        elif target_property == DM_ADD:
            print('Adding pings by dm.')
            new_names = verify_names(
                parse_input(new_value_input.content, PARTICIPANTS_BREAKPOINTS),
                self._names_to_pings
            )
            updated_meeting.add_names(new_names, ATTRIBUTE_DM)
        
        # If removing pings by dm:
        elif target_property == DM_REMOVE:
            print('Removing pings by dm.')
            new_names = parse_input(
                new_value_input.content, PARTICIPANTS_BREAKPOINTS
            )
            updated_meeting.remove_names(new_names, ATTRIBUTE_DM)
        
        # Otherwise, unkown target property.
        else:
            print('Unknown target property, terminating.')
            return

        # STEP 4: Confirmation.
        print('New value set on updated meeting, sending confirmation view.')

        await interaction.followup.send(
            content = build_confirmation_content(updated_meeting),
            view = build_confirmation_view(
                meetings,
                target_meeting,
                updated_meeting,
                names_to_pings,
                target_property,
                new_names
            )
        )


def build_target_property_content(target_property: str) -> str:
    return (
        target_property if target_property not in (
            PARTICIPANTS_ADD, PARTICIPANTS_REMOVE, DM_ADD, DM_REMOVE
        ) else
        
        ATTRIBUTE_PARTICIPANTS if target_property in (
            PARTICIPANTS_ADD, PARTICIPANTS_REMOVE
        ) else
        
        'pings by DM'
    )


# ON RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    recurrence: str,
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    names_to_pings: dict[str: str],
    target_property: str,
    **_
) -> None:
    print('In on recurrence select.')

    # Set recurrence.
    updated_meeting.set_recurrence(recurrence if recurrence != NULL_SELECT_VALUE else '')

    # STEP 4: Confirmation.
    print('New value set on updated meeting, sending confirmation view.')

    await interaction.response.edit_message(
        content = build_confirmation_content(updated_meeting),
        view = build_confirmation_view(
            meetings,
            target_meeting,
            updated_meeting,
            names_to_pings,
            target_property
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    names_to_pings: dict[str: str],
    target_property: str,
    updated_names: list[str] = [],
    **_
) -> None:
    print('In on confirm, removing original meeting.')
    print(f'In on confirm: {updated_names}')

    # Remove original meeting.
    remove_err = remove_meeting(meetings, target_meeting)
    if remove_err:
        await interaction.response.edit_message(
            content = f'{remove_err}\nNothing to edit.',
            view = None
        )
        print('Remove error, terminating.')
        return
    
    # Add updated meeting.
    add_meeting(meetings, updated_meeting)
    save_meetings()
    print('Updated meeting added, data saved.')

    await interaction.response.edit_message(
        content = (
            f'Changes for the {build_target_property_content(target_property)} for {target_meeting.get_title(True)} have been __saved__! ✨\n'
            f'{updated_meeting.to_discord(full = True)}'
            f'{(
                f'\n\n{get_ping_str(updated_meeting.get_participants(), names_to_pings)}'
                if target_property == ATTRIBUTE_TIME else

                f'\n\n{get_ping_str(updated_names, names_to_pings)}'
                if updated_names else

                ''
            )}'
        ),
        view = None
    )

    failed_dm_users = await dm_meeting(interaction.client,
        updated_meeting.get_dm()
        if target_property == ATTRIBUTE_TIME else

        [name for name in updated_names if name in updated_meeting.get_dm()]
        if target_property in (PARTICIPANTS_ADD, PARTICIPANTS_REMOVE) else

        updated_names
        if target_property in (DM_ADD, DM_REMOVE) else

        [],
        (
            f'Letting you know that {(
                'the **time for a meeting you\'re in has changed**'
                if target_property == ATTRIBUTE_TIME else

                'you\'ve been **added to a meeting**'
                if target_property == PARTICIPANTS_ADD else

                'you\'ve been **removed from a meeting**'
                if target_property == PARTICIPANTS_REMOVE else

                'you\'ve been **added to the list of pings by DM** for a meeting'
                if target_property == DM_ADD else

                'you\'ve been **removed from the list of pings by DM** for a meeting'
            )}:\n'
            f'{updated_meeting.to_discord(
                full = target_property in (ATTRIBUTE_TIME, PARTICIPANTS_ADD, DM_ADD),
            )}'
        ), names_to_pings)

    if failed_dm_users: await interaction.followup.send(
        build_failed_dm_err(failed_dm_users)
    )
    print('DMs have been sent.')

    print('Edit meeting command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    await interaction.response.edit_message(
        content = f'Changes for {target_meeting.get_title(True)} have been __discarded__! 🗑️',
        view = None
    )

    print('Edit meeting command end, cancelled.')


def build_confirmation_content(updated_meeting: Meeting) -> str:
    return (
        'Updated meeting:\n'
        f'{updated_meeting.to_discord(full = True,)}\n\n'
        'Would you like to save these changes?'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    names_to_pings: dict[str: str],
    target_property: str,
    updated_names: list[str]
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        target_meeting = target_meeting,
        updated_meeting = updated_meeting,
        names_to_pings = names_to_pings,
        target_property = target_property,
        updated_names = updated_names
    )
