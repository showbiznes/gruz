import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timezone, timedelta
import os

# dotenv опционален — на хостинге переменные задаются через панель
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

# Московское время UTC+3 (фиксированное смещение, без багов pytz)
MSK = timezone(timedelta(hours=3))

# Расписание оповещений (МСК)
SCHEDULE = [
    time(hour=12, minute=0, tzinfo=MSK),   # 12:00 МСК
    time(hour=18, minute=0, tzinfo=MSK),   # 18:00 МСК
]

# Сообщения для каждого времени
MESSAGES = {
    "12:00": (
        "📦 **Сброс груза!**\n\n"
        "||@everyone||\n\n"
        "⏰ **12:00 МСК** — Груз на карте!"
    ),
    "18:00": (
        "📦 **Сброс груза!**\n\n"
        "||@everyone||\n\n"
        "⏰ **18:00 МСК** — Груз на карте!"
    ),
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Бот {bot.user} запущен и готов к работе!")
    print(f"📢 Канал для оповещений: {CHANNEL_ID}")
    print(f"⏰ Расписание (МСК): 12:00, 18:00")

    if not cargo_drop_notification.is_running():
        cargo_drop_notification.start()


@tasks.loop(time=SCHEDULE)
async def cargo_drop_notification():
    """Отправляет оповещение о сбросе груза по расписанию."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"❌ Канал {CHANNEL_ID} не найден!")
        return

    now = datetime.now(MSK)
    current_time = now.strftime("%H:%M")

    message = MESSAGES.get(current_time)
    if message is None:
        # Фоллбэк — универсальное сообщение
        message = (
            f"📦 **Сброс груза!**\n\n"
            f"||@everyone||\n\n"
            f"⏰ **{current_time} МСК** — Груз на карте!"
        )

    await channel.send(message)
    print(f"📨 Оповещение отправлено в {current_time} МСК")


@cargo_drop_notification.before_loop
async def before_cargo_drop():
    """Ждём полной готовности бота перед запуском таймера."""
    await bot.wait_until_ready()


@bot.command(name="время")
async def show_time(ctx):
    """Показывает текущее московское время."""
    now = datetime.now(MSK)
    await ctx.send(f"🕐 Текущее московское время: **{now.strftime('%H:%M:%S')}**")


@bot.command(name="расписание")
async def show_schedule(ctx):
    """Показывает расписание сбросов груза."""
    schedule_text = (
        "📋 **Расписание сбросов груза (МСК):**\n\n"
        "🕐 **12:00** — Сброс груза на карте\n"
        "🕕 **18:00** — Сброс груза на карте"
    )
    await ctx.send(schedule_text)


@bot.command(name="тест")
@commands.has_permissions(administrator=True)
async def test_notification(ctx):
    """Тестовое оповещение (только для администраторов)."""
    now = datetime.now(MSK)
    await ctx.send(
        f"🧪 **Тестовый сброс груза!**\n\n"
        f"||@everyone||\n\n"
        f"⏰ **{now.strftime('%H:%M')} МСК** — Тестовое оповещение!"
    )


if __name__ == "__main__":
    if not TOKEN:
        print("❌ Ошибка: DISCORD_TOKEN не задан!")
        print("Создайте файл .env и укажите DISCORD_TOKEN=ваш_токен")
        exit(1)

    if CHANNEL_ID == 0:
        print("❌ Ошибка: CHANNEL_ID не задан!")
        print("Укажите CHANNEL_ID=id_канала в файле .env")
        exit(1)

    bot.run(TOKEN)
