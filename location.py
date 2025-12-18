import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import requests
import os
API_TOKEN = "Sample"
bot = telebot.TeleBot(API_TOKEN)
os.makedirs('Data', exist_ok=True)
hideboard = ReplyKeyboardRemove()
commands = {
    'start'     : 'شروع ربات / Start the bot',
    'help'      : 'نمایش راهنما / Show help',
    'location'  : 'دریافت موقعیت مکانی / Get your location info',
}
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(f"{m.chat.first_name} [{m.chat.id}]: {m.text}")
        elif m.content_type == 'location':
            print(f"{m.chat.first_name} [{m.chat.id}]: sent location")
bot.set_update_listener(listener)
@bot.message_handler(commands=['start'])
def command_start(message):
    cid = message.chat.id
    bot.send_message(
        cid,
        "سلام 👋\n"
        "به *ربات مکان‌یاب تلگرام* خوش آمدید! 🌍\n"
        "من می‌تونم موقعیت مکانی شما رو به *نام شهر و کشور* تبدیل کنم.\n\n"
        "برای شروع، از دستور /location استفاده کنید.",
        parse_mode="Markdown"
    )
@bot.message_handler(commands=['help'])
def command_help(message):
    cid = message.chat.id
    text = "📘 *راهنمای دستورات:*\n\n"
    for c, d in commands.items():
        text += f"/{c} → {d}\n"
    bot.send_message(cid, text, parse_mode="Markdown")
@bot.message_handler(commands=['location'])
def command_location(message):
    cid = message.chat.id
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_location = KeyboardButton("📍 ارسال موقعیت من", request_location=True)
    markup.add(btn_location)
    bot.send_message(cid, "لطفاً موقعیت مکانی خود را ارسال کنید:", reply_markup=markup)
@bot.message_handler(content_types=['location'])
def handle_location(message):
    cid = message.chat.id
    location = message.location
    lat = location.latitude
    lon = location.longitude
    print(f"📍 Location received: {lat}, {lon}")
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&zoom=10&addressdetails=1"
        headers = {"User-Agent": "LocationFinderBot/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get("address", {})
            city = address.get("city") or address.get("town") or address.get("village") or "نامشخص"
            country = address.get("country", "نامشخص")

            msg = (
                f"🏙️ *مکان تقریبی شما:*\n"
                f"📌 شهر: {city}\n"
                f"🌍 کشور: {country}\n"
                f"📍 مختصات: ({lat:.4f}, {lon:.4f})"
            )
            bot.send_message(cid, msg, parse_mode="Markdown", reply_markup=hideboard)
        else:
            bot.send_message(cid, "⚠️ خطا در ارتباط با سرور Nominatim.", reply_markup=hideboard)
    except Exception as e:
        print("❌ Location Error:", e)
        bot.send_message(cid, "⚠️ خطا در پردازش موقعیت مکانی.", reply_markup=hideboard)
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, "دستور نامعتبر است. برای راهنما از /help استفاده کن.", reply_markup=hideboard)
bot.infinity_polling()
