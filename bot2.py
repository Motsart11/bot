import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = "7772821435:AAH2hHaxGi3hkrFmFUQp90pzCR0AvfZwWJc"  # Замените на ваш реальный токен

# Функция для отправки главного меню
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = "Выберите действие:"
    keyboard = [
        [InlineKeyboardButton("Пройти тест ✍️", callback_data="test")],
        [InlineKeyboardButton("Информация о РПП 📖", callback_data="info")],
        [InlineKeyboardButton("Питание 🍽️", callback_data="nutrition")],
        [InlineKeyboardButton("О нас ℹ️", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Пробуем отправить сообщение с фото (файл main.jpg должен быть в той же директории)
    try:
        with open("main.jpg", "rb") as photo:
            await context.bot.send_photo(
                chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup
            )
    except Exception:
        # Если фото недоступно — отправляем только текст
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

# Функция-обработчик для кнопки "Назад"
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Удаляем текущее сообщение с информацией
    await query.message.delete()
    # Отправляем главное меню
    await send_main_menu(update, context)

# Основной обработчик inline-кнопок
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = update.effective_chat.id
    # Удаляем сообщение, из которого нажата кнопка
    await query.message.delete()

    if data == "test":
        text = "Начинаем тест. Здесь будут вопросы и варианты ответов."
        # В данном примере просто текст. Реальную логику теста можно реализовать отдельно.
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    elif data == "info":
        text = (
            "Расстройство пищевого поведения (РПП) — это психическое заболевание, "
            "негативно влияющее на физическое и психическое здоровье человека. "
            "Подробности: [текст с информацией о РПП]."
        )
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("brr.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup
                )
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    elif data == "nutrition":
        text = (
            "Как посчитать свою норму калорий?\n\n"
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
                await context.bot.send_photo(
                    chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup
                )
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    elif data == "about":
        text = (
            "О нас:\n\n"
            "Козлова Валерия Витальевна — создатель бота.\n"
            "Тест разработан на основе методик психотерапии и Eating Attitudes Test (EAT-26)."
        )
        keyboard = [[InlineKeyboardButton("Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("face.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup
                )
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)

    # Дополнительные разделы для "Питание"
    elif data == "products":
        text = (
            "Полезные продукты:\n\n"
            "• Овощи, фрукты, ягоды\n"
            "• Сухофрукты\n"
            "• Зерновой хлеб и т.д."
        )
        keyboard = [[InlineKeyboardButton("Назад", callback_data="nutrition")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            with open("fructs.jpg", "rb") as photo:
                await context.bot.send_photo(
                    chat_id=chat_id, photo=photo, caption=text, reply_markup=reply_markup
                )
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
        # Если не распознали callback — возвращаем главное меню
        await send_main_menu(update, context)

# Команда /start для вывода главного меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update, context)

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Обработчик для кнопки "Назад"
    application.add_handler(CallbackQueryHandler(back_to_menu, pattern=r"^back$"))
    # Обработчик для остальных кнопок меню
    application.add_handler(CallbackQueryHandler(handle_menu))
    application.run_polling()

if __name__ == "__main__":
    main()
