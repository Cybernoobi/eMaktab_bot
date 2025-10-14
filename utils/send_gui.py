import sys, os
import asyncio

from aiogram import Bot
from aiogram.types import FSInputFile
import PySide6.QtAsyncio as QtAsyncio
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QFileDialog, QComboBox, QMessageBox
)

os.environ["CONFIG_FILE_PATH"] = "../config.toml"

from config_reader import BotConfig, get_config
from database.utils import get_all_tg_users, get_all_em_users

# Асинхронный бот
bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
bot = Bot(bot_config.token.get_secret_value())


def get_all_users():
    """Считывает всех пользователей из файла users.txt"""
    try:
        with open("users.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip().isdigit()]
    except FileNotFoundError:
        return []


class BotSender(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📨 Telegram Sender (PySide6 + QtAsyncio)")
        self.resize(420, 420)
        self.file_path = None

        layout = QVBoxLayout()

        layout.addWidget(QLabel("ID пользователя (или all):"))
        self.target_input = QLineEdit()
        layout.addWidget(self.target_input)

        layout.addWidget(QLabel("Стиль сообщения:"))
        self.style_box = QComboBox()
        self.style_box.addItems(["HTML", "Markdown"])
        layout.addWidget(self.style_box)

        layout.addWidget(QLabel("Текст сообщения:"))
        self.message_input = QTextEdit()
        layout.addWidget(self.message_input)

        self.file_button = QPushButton("📎 Прикрепить файл (опционально)")
        self.file_button.clicked.connect(self.select_file)
        layout.addWidget(self.file_button)

        self.send_button = QPushButton("🚀 Отправить")
        self.send_button.clicked.connect(lambda: asyncio.ensure_future(self.on_send_clicked()))
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            self.file_path = file_path
            self.file_button.setText(f"✅ Файл выбран: {file_path.split('/')[-1]}")

    def show_message(self, text: str):
        msg = QMessageBox(self)
        msg.setWindowTitle("Результат")
        msg.setText(text)
        msg.exec()

    async def on_send_clicked(self):
        """Асинхронная отправка сообщений"""
        text = self.message_input.toPlainText().strip()
        if not text:
            self.show_message("❌ Введите текст сообщения!")
            return

        target = self.target_input.text().strip()
        if not target:
            self.show_message("❌ Укажите ID пользователя или 'all'")
            return

        parse_mode = self.style_box.currentText()
        file_path = self.file_path

        if target.lower() == "all":
            users = await get_all_tg_users()
            for uid in users:
                await self._send_to_user(str(uid.telegram_id), text, parse_mode, file_path)
        else:
            await self._send_to_user(target, text, parse_mode, file_path)

        self.show_message("✅ Сообщения успешно отправлены!")
        await bot.session.close()

    async def _send_to_user(self, user_id: str, text: str, parse_mode: str, file_path: str | None):
        try:
            if file_path:
                document = FSInputFile(file_path)
                await bot.send_document(int(user_id), document=document, caption=text, parse_mode=parse_mode)
            else:
                await bot.send_message(int(user_id), text, parse_mode=parse_mode)
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user_id}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = BotSender()
    main_window.show()

    QtAsyncio.run(handle_sigint=True)
