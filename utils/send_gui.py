import asyncio
import time
from typing import Literal
import os

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

os.environ["CONFIG_FILE_PATH"] = r"..\config.toml"

import flet as ft
import flet.core.textfield as tf
from flet.core.types import FontWeight, AppView
from flet import AppBar, ElevatedButton, Page, Text, View, Colors
from aiogram import Bot
from config_reader import BotConfig, get_config
from database.utils import get_all_users

# ---------- Настройки ----------
parse_mode_literal = Literal["Markdown", "MarkdownV2", "HTML"]
parse_mode_list = ["Markdown", "MarkdownV2", "HTML"]

# ---------- Глобальные переменные ----------
bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")
# bot = Bot(bot_config.token.get_secret_value())
bot = Bot("6863662911:AAEe-sRO3fjvs6oGbWdmwYqroo_7WN_ov40")


# ---------- Отправка сообщений ----------
async def send_message_to_user(user_id: int, text: str, parse_mode: parse_mode_literal | str):
    await bot.send_message(chat_id=user_id, text=text, parse_mode=parse_mode)


async def send_message_to_all(text: str, parse_mode: parse_mode_literal | str, log_output: ft.Text):
    users = await get_all_users("tg")
    sent = 0
    for user in users:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode=parse_mode)
            sent += 1
        except Exception as e:
            log_output.value += f"\nОшибка при отправке {user.full_name}: {e}"
    log_output.value += f"\n✅ Сообщение отправлено {sent} пользователям"
    log_output.update()


# ---------- Главная страница ----------
def main(page: ft.Page):
    page.title = "Telegram Sender"
    page.scroll = ft.ScrollMode.AUTO
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.vertical_alignment = ft.MainAxisAlignment.START

    # --- Поля ---
    message_field = ft.TextField(label="Текст сообщения", multiline=True, expand=True, min_lines=5)
    user_id_field = ft.TextField(
        label="ID пользователя (оставь пустым, чтобы отправить всем)",
        keyboard_type=tf.KeyboardType.NUMBER,
    )

    mode_dropdown = ft.Dropdown(
        label="Режим форматирования",
        options=[ft.dropdown.Option(i) for i in parse_mode_list],
        value=bot_config.parse_mode if hasattr(bot_config, "parse_mode") else "HTML",
    )

    log_output = ft.Text(value="", selectable=True)
    preview_box = ft.Text("Предпросмотр появится здесь", selectable=True, color=ft.Colors.BLACK)

    # --- Обновление предпросмотра ---
    def update_preview(_=None):
        text = message_field.value.strip()
        mode = mode_dropdown.value
        if not text:
            preview_box.value = "Предпросмотр пуст..."
        else:
            if mode.startswith("Markdown"):
                preview_box.value = text.replace("**", "𝗯𝗼𝗹𝗱").replace("__", "italic")
            else:
                preview_box.value = text.replace("<b>", "").replace("</b>", "").replace("<i>", "")
        preview_box.update()

    message_field.on_change = update_preview
    mode_dropdown.on_change = update_preview

    # --- Кнопка отправки ---
    async def on_send_click(_):
        text = message_field.value.strip()
        mode = mode_dropdown.value
        user_id = user_id_field.value.strip()

        if not text:
            log_output.value += "\n❌ Введите текст!"
            log_output.update()
            return

        log_output.value += "\n⏳ Отправка..."
        log_output.update()

        if user_id:
            try:
                await send_message_to_user(int(user_id), text, mode)
                log_output.value += f"\n✅ Сообщение отправлено пользователю {user_id}"
            except Exception as ex:
                log_output.value += f"\n❌ Ошибка: {ex}"
        else:
            await send_message_to_all(text, mode, log_output)

        log_output.update()

    send_button = ft.ElevatedButton(text="Отправить", on_click=on_send_click)

    # --- Навигация ---
    def open_settings(_):
        page.go("/settings")

    settings_button = ft.ElevatedButton(
        text="Настройки",
        icon=ft.Icons.SETTINGS,
        on_click=open_settings,
    )

    # --- Основная страница ---
    main_view = ft.View(
        "/",
        [
            ft.Text("Отправка сообщений", size=22, weight=FontWeight.BOLD),
            message_field,
            user_id_field,
            mode_dropdown,
            send_button,
            ft.Divider(),
            ft.Text("Предпросмотр:", weight=FontWeight.BOLD),
            ft.Container(preview_box, bgcolor=ft.Colors.GREY_200, padding=10, border_radius=5),
            ft.Divider(),
            ft.Text("Лог:", weight=FontWeight.BOLD),
            log_output,
            ft.Divider(),
            settings_button,
        ],
        scroll=ft.ScrollMode.AUTO,
    )

    # ---------- Страница настроек ----------
    token_field = ft.TextField(
        label="Токен бота",
        value=bot_config.token.get_secret_value(),
        password=True,
        can_reveal_password=True,
    )
    parse_mode_settings = ft.Dropdown(
        label="Режим форматирования по умолчанию",
        options=[ft.dropdown.Option(i) for i in parse_mode_list],
        value=bot_config.parse_mode if hasattr(bot_config, "parse_mode") else "HTML",
    )

    def save_settings(_):
        # Здесь можно сохранить настройки обратно в config.toml
        log_output.value += f"\n💾 Настройки сохранены: {parse_mode_settings.value}"
        log_output.update()
        page.go("/")

    settings_view = ft.View(
        "/settings",
        [
            ft.Text("Настройки", size=22, weight=FontWeight.BOLD),
            token_field,
            parse_mode_settings,
            ft.Row(
                [
                    ft.ElevatedButton(text="💾 Сохранить", on_click=save_settings),
                    ft.ElevatedButton(text="↩ Назад", on_click=lambda _: page.go("/")),
                ]
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
    )

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(main_view)
        elif page.route == "/settings":
            page.views.append(settings_view)
        page.update()

    page.on_route_change = route_change
    page.go(page.route)


def adaptive_app(page: ft.Page):
    title = "Bot Sender"

    page.title = title
    page.adaptive = True

    page.appbar = ft.AppBar(
        title=ft.Text(title),
        bgcolor=ft.Colors.with_opacity(0.04, ft.CupertinoColors.SYSTEM_BACKGROUND),
    )

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Главная"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Настройки"),
        ],
        border=ft.Border(
            top=ft.BorderSide(color=ft.CupertinoColors.SYSTEM_GREY2, width=0)
        ),
    )

    def set_theme(e):
        if e.data is True:
            page.theme_mode = ft.ThemeMode.DARK
        elif e.data is False:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

    def route_change(e):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    ft.SafeArea(
                        ft.Column(
                            [
                                ft.Checkbox(value=False, label="Dark Mode", on_change=set_theme),
                                ft.Text("First field:"),
                                ft.TextField(keyboard_type=ft.KeyboardType.TEXT),
                                ft.Text("Second field:"),
                                ft.TextField(keyboard_type=ft.KeyboardType.TEXT),
                                ft.Switch(label="A switch"),
                                ft.FilledButton(content=ft.Text("Adaptive button")),
                                ft.Text("Text line 1"),
                                ft.Text("Text line 2"),
                                ft.Text("Text line 3"),
                            ]
                        )
                    )
                ],
            )
        )
        if page.route == "/settings":
            page.views.append(
                View(
                    "/settings",
                    [
                        AppBar(title=Text("Store"), bgcolor=Colors.SURFACE_VARIANT),
                        ElevatedButton("Go Home", on_click=lambda _: page.go("/")),
                    ],
                )
            )
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)

# ---------- CLI ----------
async def send_all(msg: str, ids: list[int] = None):
    ids = ids or await get_all_users("em", only_id=True)
    for chat_id in ids:
        try:
            bot_msg = await bot.send_message(chat_id, msg, parse_mode="HTML")
            print(f"Успешно {chat_id=}, {bot_msg.message_id=}")
        except TelegramBadRequest as e:
            print("Пропускаем " + str(chat_id), e)
            continue
        except TelegramForbiddenError as e:
            print("Бот заблокирован у пользователя " + str(chat_id), e)
            continue
        except TelegramRetryAfter as e:
            print(str(e.args[1]).split(" "))
            timeout = int(str(e.args[1]).split(" ")[-1])
            await asyncio.sleep(timeout)
            await bot.send_message(chat_id, msg, parse_mode="HTML")
        # finally:
        #     await bot.close()
# ---------- Запуск ----------
if __name__ == '__main__':
    # ft.app(target=main, host="0.0.0.0", port=8080, view=AppView.WEB_BROWSER)
    asyncio.run(send_all("""
Бот был обновлён до версии beta 0.0.3
Если обнаружите ошибки пожалуйста сообщите разработчика @Cybernoobi

Что изменилось?<blockquote>
1. Добавлена команда /me
2. Кнопка "Выбрать день" в "⌛️ Оценки" работает
3. Ошибки теперь отправляются автоматически разработчику
</blockquote>
    """))