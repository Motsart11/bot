import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "7037917294:AAG5GFqqg0nWZ2mWk8CzVdsucu8eQYXFkMM"  # Замените на ваш реальный токен

# --- Функция для отправки главного меню (с фото main.jpg, если есть) ---
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если update – callback_query, берем chat_id из него
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id = update.message.chat.id
    else:
        chat_id = update.effective_chat.id
    text = ("Привет! Я бот, который может помочь вам с диагностикой расстройства пищевого поведения, "
            "дать полезную информацию о питании и многое другое. Чем могу быть полезен?")
    keyboard = [
        [InlineKeyboardButton("Пройти тест ✍️", callback_data="test")],
        [InlineKeyboardButton("Информация о РПП 📖", callback_data="info")],
        [InlineKeyboardButton("Питание 🍽️", callback_data="nutrition")],
        [InlineKeyboardButton("О нас ℹ️", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        with open("main.jpg", "rb") as photo:
            await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup)
    except Exception:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# --- Функция-обработчик для кнопки "Назад" ---
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    await send_main_menu(update, context)

# --- Тестовые вопросы ---
ALL_QUESTIONS = [
    {"text": "Ваш пол? (этот вопрос должен оцениваться 0)", "answers": [("М", 0), ("Ж", 0)]},
    {"text": "Вы занимаетесь спортом", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я испытываю ужас при мысли об избыточном весе", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я избегаю приём пищи, когда голодна", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я сильно озабочен(а) вопросами еды", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "У меня были эпизоды переедания и меня тошнило", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я ем маленькими порциями", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я знаю количество калорий в еде, которую ем", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я избегаю еду с большим содержанием углеводов", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Мне часто говорят, что я мало ем", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я часто заедаю стресс", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "У меня бывает рвота после еды", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я испытываю вину после съеденной еды", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Меня часто преследуют мысли о похудении", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я хожу в зал, чтобы отработать съеденные калории", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я часто слышу, что мне нужно набрать вес", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "У меня есть ощущение, что другие заставляют меня принимать пищу", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "В детстве меня дразнили из-за веса", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я часто следую диетам, чтобы похудеть", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я люблю вкусно поесть", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Новые дорогие продукты доставляют мне удовольствие", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я предпочитаю, чтобы мой желудок был пуст", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "В детстве Вы занимались танцами/спортом, и Вам нужно было следить за весом", "answers": [("Да", 4), ("Скорее да", 3), ("Скорее нет", 2), ("Нет", 1)]},
    {"text": "У меня были мысли о суициде", "answers": [("Да", 4), ("Скорее да", 3), ("Скорее нет", 2), ("Нет", 1)]},
    {"text": "Я принимал(а) антидепрессанты", "answers": [("Да", 4), ("Скорее да", 3), ("Скорее нет", 2), ("Нет", 1)]},
    {"text": "Я часто переживаю из-за пустяков", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я часто чувствую дискомфорт на учёбе/работе", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Мне сложно заснуть", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "У меня часто мысли в голове перед сном, которые мешают заснуть", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я очень боюсь возможных неудач", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Я чувствую себя ненужным (ой)", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
    {"text": "Мне порой кажется, что ничего не стою", "answers": [("Всегда", 4), ("Иногда", 3), ("Редко", 2), ("Никогда", 1)]},
]

# --- Сопоставление диапазонов баллов с картинками ---
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

# --- Функция для отправки тестового вопроса ---
async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        chat_id = update.message.chat_id
    else:
        chat_id = update.callback_query.message.chat_id
    user_data = context.user_data.setdefault(chat_id, {})
    if "question_index" not in user_data:
        user_data["question_index"] = 0
        user_data["score"] = 0
    q_index = user_data["question_index"]
    question = ALL_QUESTIONS[q_index]
    text = f"Вопрос {q_index+1}/{len(ALL_QUESTIONS)}:\n{question['text']}"
    buttons = [[InlineKeyboardButton(ans, callback_data=str(val))] for ans, val in question["answers"]]
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- Callback-хэндлер для ответов на тестовые вопросы ---
async def handle_test_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    user_data = context.user_data.setdefault(chat_id, {})
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
        photo_path = get_result_photo_path(total_score)
        with open(photo_path, "rb") as photo_file:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=photo_file,
                caption=f"✅ Тест завершён!\nВаш результат: {total_score} баллов\n\n{result_text}"
            )
        # Очищаем данные теста
        user_data.pop("question_index", None)
        user_data.pop("score", None)
        # Отправляем сообщение с inline-кнопкой "Назад" для возврата в главное меню
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text="Нажмите 'Назад', чтобы вернуться в главное меню.", reply_markup=reply_markup)
    else:
        await send_question(update, context)

# --- Основной обработчик inline-кнопок для навигации ---
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    await query.message.delete()
    if data == "test":
        context.user_data[chat_id] = {"score": 0, "question_index": 0}
        await send_question(update, context)
    elif data == "info":
        text = (
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
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("brr.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup)
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    elif data == "nutrition":
        text = (
            "Как посчитать свою норму калорий?\n\n"
            "Для расчёта нормы калорий можно использовать формулу Харриса‑Бенедикта. Она определяет базальную скорость метаболизма (BMR) — количество калорий, необходимых для нормальной работы организма.\n\n"
            "Формула для мужчин:\n"
            "BMR = 88,36 + (13,4 × вес в кг) + (4,8 × рост в см) – (5,7 × возраст в годах).\n\n"
            "Формула для женщин:\n"
            "BMR = 447,6 + (9,2 × вес в кг) + (3,1 × рост в см) – (4,3 × возраст в годах)."
        )
        keyboard = [
            [InlineKeyboardButton("Полезные продукты", callback_data="products")],
            [InlineKeyboardButton("Расчёт калорий", callback_data="calories")],
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("salat.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup)
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    elif data == "about":
        text = (
            "Козлова Валерия Витальевна – создатель телеграм-бота\n\n"
            "Наш тест создан на основе теста по методике американского психотерапевта Аарона Бека, "
            "который помогает определить уровень тревожности, и Eating Attitudes Test (EAT-26), "
            "разработанного Институтом психиатрии Кларка в Торонто в 1979 году. Тест широко используется для диагностики РПП психиатрами и психотерапевтами по всему миру. "
            "Тест EAT-26 был разработан в первую очередь для определения анорексии и булимии, но также помогает выявить другие проблемы, включая ограничительное и компульсивное переедание.\n\n"
            "Результаты теста могут помочь в выявлении симптоматики, но не могут считаться диагнозом. "
            "Если вы обнаружили тревожные сигналы, обязательно обратитесь за медицинской помощью.\n\n"
            "По всем интересующим вопросам обращайтесь по эл. почте: Kozlovalera2005111@gmail.com"
        )
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("face.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup)
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    elif data == "products":
        text = (
            "Полезные продукты:\n\n"
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
        keyboard = [[InlineKeyboardButton("Назад", callback_data="nutrition")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("fructs.jpg", "rb") as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup)
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    elif data == "calories":
        text = (
            "Для расчёта калорий введите команду /calc и следуйте инструкциям.\n"
            "Например, вы можете ввести свои данные и получить результат."
        )
        keyboard = [[InlineKeyboardButton("Назад", callback_data="nutrition")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
    else:
        await send_main_menu(update, context)

# --- Команда /start для вывода приветственного сообщения с inline-кнопками ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = ("Привет! Я бот, который может помочь вам с диагностикой расстройства пищевого поведения, "
            "дать полезную информацию о питании и многое другое.")
    keyboard = [
        [InlineKeyboardButton("Пройти тест ✍️", callback_data="test")],
        [InlineKeyboardButton("Информация о РПП 📖", callback_data="info")],
        [InlineKeyboardButton("Питание 🍽️", callback_data="nutrition")],
        [InlineKeyboardButton("О нас ℹ️", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Хэндлер для тестовых ответов (числовые callback_data)
    application.add_handler(CallbackQueryHandler(handle_test_answer, pattern=r"^\d+(\.\d+)?$"))
    # Хэндлер для кнопки "Назад" – регистрируем его первым, чтобы он срабатывал при совпадении callback "back"
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern=r"^back$"))
    # Хэндлер для остальных inline‑кнопок (навигация)
    application.add_handler(CallbackQueryHandler(handle_menu))
    application.run_polling()

if __name__ == "__main__":
    main()
