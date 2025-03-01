import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# Логирование
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7772821435:AAH2hHaxGi3hkrFmFUQp90pzCR0AvfZwWJc"  # Замените на реальный токен

# --- Пример вопросов для теста (если нужны) ---
ALL_QUESTIONS = [
    {"text": "Ваш пол? (не влияет на итоговый балл)", "answers": [("М", 0), ("Ж", 0)]},
    {"text": "Вы занимаетесь спортом?", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я испытываю ужас при мысли об избыточном весе", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я избегаю приём пищи, когда голоден(а)", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Меня часто преследуют мысли о похудении", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    # ... остальные вопросы ...
]

# Добавляем сопоставление диапазона баллов с фото
RESULT_PHOTOS = {
    "low": "heartcat.jpg",       # для score <= 60
    "medium": "dog.jpg",         # для score <= 80
    "high": "stepa.jpg",         # для score <= 124
    "critical": "stepa.jpg"      # для score >= 125
}

def get_test_result_text(score: float) -> str:
    if score <= 60:
        return "✅ 0–60 баллов: Поздравляем! У вас отличные отношения с едой."
    elif score <= 80:
        return "⚠️ 61–80 баллов: У вас спокойное отношение к еде, но беспокойства по поводу веса."
    elif score <= 124:
        return "🚨 80-124 баллов: Возможно, вам стоит обратиться к специалисту."
    else:
        return "❗ 125+ баллов: У вас серьёзные проблемы с пищевым поведением."

def get_result_photo_path(score: float) -> str:
    if score <= 60:
        return RESULT_PHOTOS["low"]
    elif score <= 80:
        return RESULT_PHOTOS["medium"]
    elif score <= 124:
        return RESULT_PHOTOS["high"]
    else:
        return RESULT_PHOTOS["critical"]

def get_main_menu():
    return ReplyKeyboardMarkup(
        [["Пройти тест ✍️", "Информация о РПП 📖"], ["Питание 🍽️", "О нас ℹ️"]],
        resize_keyboard=True,
    )

# --- Функция для кеширования и отправки фото ---
PHOTO_CACHE = {}

async def send_cached_photo(bot, chat_id, image_path, caption):
    if image_path in PHOTO_CACHE:
        file_id = PHOTO_CACHE[image_path]
        await bot.send_photo(chat_id=chat_id, photo=file_id, caption=caption)
    else:
        with open(image_path, "rb") as photo_file:
            message = await bot.send_photo(chat_id=chat_id, photo=photo_file, caption=caption)
        PHOTO_CACHE[image_path] = message.photo[-1].file_id

# --- Функция для отправки тестового вопроса ---
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    user_data = context.user_data[chat_id]
    question_index = user_data["question_index"]
    question = ALL_QUESTIONS[question_index]
    text = f"Вопрос {question_index+1}/{len(ALL_QUESTIONS)}:\n{question['text']}"
    buttons = [
        [InlineKeyboardButton(answer, callback_data=str(score))]
        for answer, score in question["answers"]
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- Обработчик callback для тестовых вопросов ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id
    user_data = context.user_data[user_id]
    try:
        score = float(query.data)
    except ValueError:
        return
    user_data["score"] += score
    user_data["question_index"] += 1
    await query.message.delete()
    if user_data["question_index"] >= len(ALL_QUESTIONS):
        total_score = user_data["score"]
        result_text = get_test_result_text(total_score)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Тест завершён!\nВаш результат: {total_score} баллов\n\n{result_text}",
            reply_markup=get_main_menu()
        )
    else:
        await send_question(update, context)

# --- Обработчик для расчёта калорий (ConversationHandler) ---
STATE_GENDER, STATE_WEIGHT, STATE_HEIGHT, STATE_AGE = range(4)

async def start_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Мужчина", callback_data="calc_male"),
         InlineKeyboardButton("Женщина", callback_data="calc_female")]
    ]
    await query.edit_message_text("Выберите пол для расчёта нормы калорий:", reply_markup=InlineKeyboardMarkup(keyboard))
    return STATE_GENDER

async def handle_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gender = query.data  # "calc_male" или "calc_female"
    context.user_data["calc_gender"] = "male" if gender == "calc_male" else "female"
    await query.edit_message_text("Введите ваш вес в кг:")
    return STATE_WEIGHT

async def handle_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число для веса.")
        return STATE_WEIGHT
    context.user_data["calc_weight"] = weight
    await update.message.reply_text("Введите ваш рост в см:")
    return STATE_HEIGHT

async def handle_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число для роста.")
        return STATE_HEIGHT
    context.user_data["calc_height"] = height
    await update.message.reply_text("Введите ваш возраст:")
    return STATE_AGE

async def handle_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = float(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число для возраста.")
        return STATE_AGE
    context.user_data["calc_age"] = age
    gender = context.user_data.get("calc_gender")
    weight = context.user_data.get("calc_weight")
    height = context.user_data.get("calc_height")
    age = context.user_data.get("calc_age")
    if gender == "male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    await update.message.reply_text(f"Ваша базальная скорость метаболизма (BMR): {bmr:.2f} ккал/день.", reply_markup=get_main_menu())
    return ConversationHandler.END

async def cancel_calculation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Расчёт отменён.", reply_markup=get_main_menu())
    return ConversationHandler.END

calc_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_calculation, pattern=r"^start_calc$")],
    states={
        STATE_GENDER: [CallbackQueryHandler(handle_gender, pattern=r"^calc_")],
        STATE_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weight)],
        STATE_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_height)],
        STATE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age)]
    },
    fallbacks=[CommandHandler("cancel", cancel_calculation)]
)

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    # Инициализируем данные для теста
    context.user_data[user_id] = {"score": 0, "question_index": 0}
    await update.message.reply_text(
        "👋 Привет! Этот бот помогает определить РПП и предоставляет полезную информацию о питании.\n\n"
        "Нажмите 'Пройти тест' для начала.",
        reply_markup=get_main_menu()
    )

# --- Обработчик текстовых команд ---
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = update.message.chat_id

    if user_text == "Пройти тест ✍️":
        context.user_data[user_id] = {"score": 0, "question_index": 0}
        await send_question(update, context)
    elif user_text == "Информация о РПП 📖":
        await update.message.reply_photo(photo=open("brr.jpg", "rb"))
        info_text = (
            "Расстройство пищевого поведения (РПП) — это психическое заболевание, негативно влияющее на физическое и психическое здоровье человека, "
            "которое характеризуется ненормальным потреблением пищи.\n\n"
            "РПП включает в себя нижеследующие подтипы:\n"
            "• Нервная анорексия (НА) — сверхмалое потребление пищи, вследствие которого пациент имеет аномально низкую массу тела.\n"
            "• Нервная булимия (НБ) — чрезмерное потребление пищи, после чего следует этап очищения желудка или приём слабительных.\n"
            "• Переедание — потребление большого количества пищи за короткий промежуток времени.\n"
            "• Другие специфические подтипы.\n"
            "• Мышечная дисморфия (МД) — восприятие своего тела как слишком худого, слабого или обрюзгшего с последующей попыткой нарастить мышечную массу всеми доступными способами.\n"
            "• Пикацизм — употребление в пищу несъедобных веществ (например, земля или мел).\n"
            "• Мерицизм (руминационный синдром) — пережёвывание произвольно отрыгиваемой пищи спустя некоторое время после еды.\n"
            "• Избегание/ограничение приёма пищи (ИПП) — психическое расстройство, при котором теряется интерес к приёму некоторых видов пищи.\n\n"
            "При этом важно понимать, что ожирение не относится к РПП.\n\n"
            "У людей с расстройством пищевого поведения часто встречаются тревожные расстройства, депрессия и химические зависимости.\n"
            "• Расстройства пищевого поведения (РПП) затрагивают не менее 9% населения во всем мире. Согласно статистике 2023 года это около 70 миллионов человек.\n"
            "• Каждые 62 минуты по крайней мере один человек умирает непосредственно в результате расстройства пищевого поведения.\n"
            "• Международные исследования показывают, что всего от 5% до 15% людей с РПП обращаются за помощью; 85% сообщают, что им трудно получить доступ к лечению."
        )
        await update.message.reply_text(info_text, disable_web_page_preview=True)
    elif user_text == "Питание 🍽️":
        await update.message.reply_photo(photo=open("salat.jpg", "rb"))
        nutrition_text = (
            "Как посчитать свою норму калорий?\n\n"
            "Для расчёта нормы калорий можно использовать формулу Харриса‑Бенедикта. Она определяет базальную скорость метаболизма (BMR) — количество калорий, необходимых для нормальной работы организма.\n\n"
            "Формула для мужчин:\n"
            "BMR = 88,36 + (13,4 × вес в кг) + (4,8 × рост в см) – (5,7 × возраст в годах).\n\n"
            "Формула для женщин:\n"
            "BMR = 447,6 + (9,2 × вес в кг) + (3,1 × рост в см) – (4,3 × возраст в годах)."
        )
        keyboard = [
            [
                InlineKeyboardButton("Полезные продукты", callback_data="show_products"),
                InlineKeyboardButton("Расчёт калорий", callback_data="start_calc")
            ]
        ]
        await update.message.reply_text(nutrition_text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif user_text == "О нас ℹ️":
        caption = (
            "Козлова Валерия Витальевна – создатель телеграм-бота\n\n"
            "Наш тест создан на основе теста по методике американского психотерапевта Аарона Бека, "
            "который помогает определить уровень тревожности, и Eating Attitudes Test (EAT-26), "
            "разработанного Институтом психиатрии Кларка в Торонто в 1979 году. Тест широко используется для диагностики РПП психиатрами и психотерапевтами по всему миру. "
            "Тест EAT-26 был разработан в первую очередь для определения анорексии и булимии, но также помогает выявить другие проблемы, включая ограничительное и компульсивное переедание.\n\n"
            "Результаты теста могут помочь в выявлении симптоматики, но не могут считаться диагнозом. "
            "Если вы обнаружили тревожные сигналы, обязательно обратитесь за медицинской помощью.\n\n"
            "По всем интересующим вопросам обращайтесь по эл. почте: Kozlovalera2005111@gmail.com"
        )
        await send_cached_photo(context.bot, user_id, "face.jpg", caption)
    else:
        await update.message.reply_text("Выберите одну из кнопок для продолжения.", reply_markup=get_main_menu())

# --- Обработчик для показа полезных продуктов ---
async def handle_show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat_id
    await query.message.delete()
    with open("fructs.jpg", "rb") as photo_file:
        await context.bot.send_photo(chat_id=user_id, photo=photo_file)
    products_text = (
        "Продукты, в которых высокое содержание полезных веществ для организма:\n\n"
        "• Овощи, фрукты и ягоды – полезны для обмена веществ и пищеварения, содержат клетчатку, пищевые волокна, витамины С, А, группы В, микро- и макроэлементы.\n"
        "• Сухофрукты – горсть сухофруктов может обеспечить суточную норму витаминов и калия.\n"
        "• Зерновой хлеб – содержит микро- и макроэлементы, витамины А, Е и группы В, пищевые волокна, сложные углеводы.\n"
        "• Крупы и приготовленные из них каши – содержат медленные углеводы и являются источником насыщения и энергии.\n"
        "• Бобовые (фасоль, бобы, чечевица, горох, нут) – сочетают легкоусвояемый белок и клетчатку.\n"
        "• Яйца – их состав включает полноценный белок, холин для работы нервной системы, лютеин для поддержки зрения, все незаменимые аминокислоты, полезные жиры, комплекс минералов и витаминов.\n"
        "• Свежая зелень – содержит витамины А, В1, В2, В5, В6, В9, В12, С, Е, K, Н, РР, холин и целый набор минералов.\n"
        "• Мёд – обладает антибактериальными, противовоспалительными и антиоксидантными свойствами.\n"
        "• Растительные масла – в их составе есть олеиновая кислота, необходимая для регенерации нервных клеток, и полезные ненасыщенные жиры."
    )
    await context.bot.send_message(chat_id=user_id, text=products_text)

# --- Регистрация обработчиков ---
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_show_products, pattern=r"^show_products$"))
    application.add_handler(CallbackQueryHandler(handle_callback, pattern=r"^\d+(\.\d+)?$"))
    application.add_handler(calc_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT, handle_text))
    application.run_polling()

if __name__ == "__main__":
    main()
