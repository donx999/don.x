import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from tests import tests

# 🔑 Tokeningizni shu yerga yozing
TOKEN = "8195337626:AAH6EVM49qscyePqb13qUTm54sy5RIqyoqI"
CHANNEL_USERNAME = "@Geografiya_attestatsiya1"

bot = telebot.TeleBot(TOKEN)

# 📌 Foydalanuvchi kanalga azo bo'lganini tekshirish
def check_subscription(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_USERNAME, user_id).status
        return status in ["member", "administrator", "creator"]
    except:
        return False

# 📌 Start komandasi
@bot.message_handler(commands=["start"])
def send_welcome(message):
    if not check_subscription(message.from_user.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Kanalga qo‘shilish", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"))
        bot.send_message(message.chat.id, "❗ Botdan foydalanish uchun kanalimizga azo bo‘ling.", reply_markup=markup)
        return

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📚 5-sinf", callback_data="class_5"))
    markup.add(InlineKeyboardButton("📚 6-sinf", callback_data="class_6"))
    markup.add(InlineKeyboardButton("📚 7-sinf", callback_data="class_7"))
    markup.add(InlineKeyboardButton("📚 8-sinf", callback_data="class_8"))
    markup.add(InlineKeyboardButton("📚 9-sinf", callback_data="class_9"))
    markup.add(InlineKeyboardButton("📚 10-sinf", callback_data="class_10"))
    markup.add(InlineKeyboardButton("📚 11-sinf", callback_data="class_11"))
    markup.add(InlineKeyboardButton("🧩 Mantiqiy savollar", callback_data="logic"))
    bot.send_message(message.chat.id, "📖 Sinfni tanlang:", reply_markup=markup)

# 📌 Callback tugmalar
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith("class_"):
        sinf = call.data.split("_")[1]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📘 Matematika", callback_data=f"subject_{sinf}_matematika"))
        markup.add(InlineKeyboardButton("📗 Ona tili", callback_data=f"subject_{sinf}_ona"))
        markup.add(InlineKeyboardButton("📕 Tarix", callback_data=f"subject_{sinf}_tarix"))
        markup.add(InlineKeyboardButton("⬅️ Ortga", callback_data="back_main"))
        bot.edit_message_text(f"📚 {sinf}-sinf fanini tanlang:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("subject_"):
        _, sinf, fan = call.data.split("_")
        key = f"{sinf}_{fan}"
        if key not in tests:
            bot.answer_callback_query(call.id, "❌ Bu fanga test hali qo‘shilmagan")
            return
        start_test(call.message.chat.id, key)

    elif call.data == "logic":
        start_test(call.message.chat.id, "logic")

    elif call.data == "back_main":
        send_welcome(call.message)

# 📌 Test boshlash
user_data = {}

def start_test(chat_id, key):
    user_data[chat_id] = {"key": key, "index": 0, "score": 0}
    send_question(chat_id)

def send_question(chat_id):
    data = user_data.get(chat_id)
    if not data:
        return

    key = data["key"]
    index = data["index"]

    if index >= len(tests[key]):
        score = data["score"]
        bot.send_message(chat_id, f"✅ Test tugadi!\nSizning natijangiz: {score}/{len(tests[key])}")
        user_data.pop(chat_id, None)
        return

    q = tests[key][index]
    markup = InlineKeyboardMarkup()
    for i, option in enumerate(q["options"]):
        markup.add(InlineKeyboardButton(option, callback_data=f"answer_{i}"))
    bot.send_message(chat_id, f"❓ {q['question']}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer(call):
    data = user_data.get(call.message.chat.id)
    if not data:
        return

    index = data["index"]
    key = data["key"]
    q = tests[key][index]

    choice = int(call.data.split("_")[1])
    if choice == q["answer"]:
        data["score"] += 1
        bot.answer_callback_query(call.id, "✅ To‘g‘ri!")
    else:
        bot.answer_callback_query(call.id, f"❌ Noto‘g‘ri. To‘g‘ri javob: {q['options'][q['answer']]}")

    data["index"] += 1
    send_question(call.message.chat.id)

# 📌 Botni ishga tushirish
bot.polling()

