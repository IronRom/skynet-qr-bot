import io

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InputFile
from aiogram.types import BufferedInputFile
from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram.types import CallbackQuery

from config import Config

from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.db_requests import upsert_user, upsert_actions

from fluentogram import TranslatorRunner
from bot.dialog_widgets.widget_i18n import I18NFormat


from bot.services.service_qr_generate import service_qr_generate


user_router = Router()

class StartSG(StatesGroup):
    start = State()

class QRGenerationSG(StatesGroup):
    start = State()

async def button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=QRGenerationSG.start)

async def generate_qr(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str
):
    config: Config = dialog_manager.middleware_data["config"]
    session: AsyncSession = dialog_manager.middleware_data["session"]
    qr_bytes = await service_qr_generate(config.service_qr.service_qr_url, text)
    photo = BufferedInputFile(qr_bytes, filename="qrcode.png")
    await upsert_actions(session, message.from_user.id,
                      qr_request=text
    )
    await message.answer_photo(photo=photo)


start_dialog = Dialog(
    Window(
        I18NFormat('user-command-start'),
        Button(
            I18NFormat('qr-generate-button'), 
            id='go_qr_generation', 
            on_click=button_clicked
        ),
        state=StartSG.start
    ),
)

qr_generation_dialog = Dialog(
    Window(
        I18NFormat('qr-text-input'),
        TextInput(
            id='qr_input',
            on_success=generate_qr,
        ),
        state=QRGenerationSG.start,
    ),
)

@user_router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    dialog_manager: DialogManager,
    ):
 
    await upsert_user(session, message.from_user.id,
                      message.from_user.first_name,
                      message.from_user.last_name)
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)
