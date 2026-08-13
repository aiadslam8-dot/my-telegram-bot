import telebot
from telebot import types
import threading

# التوكن الخاص ببوتك الرئيسي (المصنع)
MAIN_TOKEN = "8861113947:AAFSV2dfGPagCB_IuRQbfGtAJ5HRd28tP2w"
main_bot = telebot.TeleBot(MAIN_TOKEN)

# تخزين حالات المستخدمين
user_states = {}
active_bots = {}

def run_user_bot(user_token, owner_id):
    try:
        user_bot = telebot.TeleBot(user_token)
        reply_waiting = {}

        @user_bot.message_handler(commands=['start'])
        def start_user_bot(msg):
            if msg.chat.id == owner_id:
                user_bot.send_message(owner_id, "أهلاً بك يا مالك البوت! 👑\nالبوت يعمل الآن وجاهز لاستقبال كافة الرسائل المجهولة.")
            else:
                user_bot.send_message(msg.chat.id, f"أهلاً بك {msg.from_user.first_name} 🤍\n\nأرسل أي شيء (نص، صورة، صوت) وسوف يصل لصاحب البوت بشكل مجهول 🔒.")

        @user_bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
        def handle_reply_btn(call):
            target_id = int(call.data.split("_")[1])
            reply_waiting[owner_id] = target_id
            user_bot.send_message(owner_id, "اكتب ردك الآن وسيتم إرساله للشخص فوراً ✍️:")

        @user_bot.message_handler(content_types=['text', 'photo', 'sticker', 'voice', 'video', 'document', 'audio'])
        def handle_sub_messages(msg):
            if msg.chat.id == owner_id:
                if owner_id in reply_waiting:
                    target_id = reply_waiting[owner_id]
                    try:
                        user_bot.copy_message(target_id, owner_id, msg.message_id)
                        user_bot.send_message(owner_id, "تم إرسال ردك بنجاح! 🚀")
                    except Exception:
                        user_bot.send_message(owner_id, "لم نتمكن من إرسال الرد.")
                    del reply_waiting[owner_id]
                else:
                    user_bot.send_message(owner_id, "أنت المالك! انتظر وصول رسائل جديدة 📥.")
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("رد ↩️", callback_data=f"reply_{msg.chat.id}"))
                
                user_bot.send_message(owner_id, "📩 رسالة مجهولة جديدة:", reply_markup=markup)
                user_bot.copy_message(owner_id, msg.chat.id, msg.message_id)
                user_bot.send_message(msg.chat.id, "تم إرسال رسالتك بنجاح! ✉️")

        user_bot.infinity_polling()
    except Exception as e:
        print(f"خطأ في تشغيل بوت المستخدم ({owner_id}): {e}")

# --- البوت الرئيسي (المصنع) ---

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("إنشاء بوت تواصل جديد 🤖"), types.KeyboardButton("مساعدة ℹ️"))
    return markup

@main_bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = f"Welcome {message.from_user.first_name} to Bot Maker! 🤍\n\nيمكنك إنشاء بوت رسائل مجهولة خاص بك مجاناً."
    main_bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@main_bot.message_handler(func=lambda message: True)
def handle_factory_messages(message):
    user_id = message.chat.id
    text = message.text.strip() if message.text else ""

    if text == "إنشاء بوت تواصل جديد 🤖":
        user_states[user_id] = "waiting_for_token"
        main_bot.send_message(user_id, "من فضلك أرسل الـ API Token الخاص ببوتك من @BotFather الآن 🔑:")

    elif text == "مساعدة ℹ️":
        help_text = (
            "خطوات إنشاء بوتك الخاص:\n"
            "1. اذهب لبوت @BotFather وأنشئ بوت جديد عبر الأمر /newbot.\n"
            "2. قم بنسخ الـ API Token الخاص ببوتك.\n"
            "3. عد هنا واضغط 'إنشاء بوت تواصل جديد 🤖' ثم أرسل الـ Token."
        )
        main_bot.send_message(user_id, help_text)

    elif user_states.get(user_id) == "waiting_for_token":
        token = text
        if ":" not in token:
            main_bot.send_message(user_id, "⚠️ الـ Token غير صحيح. تأكد من نسخه كاملاً من @BotFather.", reply_markup=main_keyboard())
            return

        try:
            test_bot = telebot.TeleBot(token)
            bot_info = test_bot.get_me()
            
            t = threading.Thread(target=run_user_bot, args=(token, user_id))
            t.daemon = True
            t.start()

            active_bots[user_id] = token
            user_states[user_id] = None

            main_bot.send_message(
                user_id, 
                f"تم إنشاء وتشغيل بوتك @{bot_info.username} بنجاح! 🎉\n\n"
                f"👈 اذهب لبوتك الجديد واضغط /start لتصبح المالك!",
                reply_markup=main_keyboard()
            )
        except Exception:
            main_bot.send_message(user_id, "❌ الـ Token غير صحيح، حاول مجدداً.", reply_markup=main_keyboard())

print("مصنع البوتات يعمل الآن...")
main_bot.infinity_polling()
