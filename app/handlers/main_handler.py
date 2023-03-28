from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import DialogRegistry, Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Button, Url, Start, Row, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from omegaconf import DictConfig

from app.configuration.config_loader import CONFIG
from app.configuration.log import get_logger
from app.fsm import states

LOGGER = get_logger(__name__, 'logs')


async def start(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.MenuSG.start, mode=StartMode.RESET_STACK)


async def user_name(dialog_manager: DialogManager, **kwargs) -> dict:
    return {'user_name': dialog_manager.event.from_user.mention_markdown()}


async def input_handler(message: Message, widget: MessageInput, manager: DialogManager):
    await message.delete()


def is_owner(event, widget, dialog_manager: DialogManager, **kwargs) -> bool:
    return CONFIG.bot.owner == dialog_manager.event.from_user.id


def gen_dialogs(data: DictConfig) -> list[Dialog]:
    dialogs = []
    for s_group_name, menus in data.Dialogs.items():
        state_group: StatesGroup = getattr(states, s_group_name)
        windows = []
        for state_name, menu_data in menus.items():
            state: State = state_group.__dict__[state_name]
            content = menu_data.content
            widgets = [MessageInput(input_handler)]

            if media := content.get('media'):
                static_media = StaticMedia(**media)
                widgets.append(static_media)

            getter = None
            if getter_name := content.get('getter'):
                getter = globals().get(getter_name)

            if text := content.get('text'):
                if getter:
                    text = Format(text)
                else:
                    text = Const(text)
                widgets.append(text)

            if buttons := menu_data.get('buttons'):
                buttons_group = []
                for row in buttons:
                    buttons_row = [
                        parse_button_data(b_data, s_group_name, state_group, state_name)
                        for b_data in row
                    ]
                    buttons_group.append(Row(*buttons_row))
                widgets.append(Group(*buttons_group))

            windows.append(Window(
                *widgets,
                state=state,
                disable_web_page_preview=True,
                getter=getter
            ))

        dialogs.append(Dialog(*windows))

    return dialogs


def parse_button_data(b_data, s_group_name, state_group, state_name) -> Button:
    button = None
    when = None
    if when_name := b_data.get('when'):
        when = globals().get(when_name, None)

    if callback := b_data.get('callback'):
        callback_data = callback.split('.')
        if len(callback_data) > 1:
            c_state_group: StatesGroup = getattr(states, callback_data[0])
            c_state = c_state_group.__dict__[callback_data[-1]]
            button = Start(
                Const(b_data.text),
                id=callback,
                state=c_state,
                mode=StartMode.RESET_STACK,
                when=when
            )
        else:
            c_state = state_group.__dict__[callback_data[-1]]
            button = SwitchTo(
                Const(b_data['text']),
                id=callback,
                state=c_state,
                when=when
            )
    elif url := b_data.get('url'):
        button = Url(
            text=Const(b_data['text']),
            url=Const(url),
            when=when
        )
    else:
        LOGGER.error(f'Wrong button data {s_group_name} -> {state_name} -> {b_data}')

    return button


def registry_dialogs(dp: Dispatcher, data):
    registry = DialogRegistry()
    dialogs = gen_dialogs(data)
    for d in dialogs:
        registry.register(d)
    registry.setup_dp(dp)


def gen_and_reg_dialogs(dp: Dispatcher, data):
    registry_dialogs(dp, data)
    dp.message.register(start, Command(commands='start'))
