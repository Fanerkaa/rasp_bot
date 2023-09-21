import requests
import io
from telegram.ext import CommandHandler, Updater
from PyPDF2 import PdfReader

import config

# Функция для извлечения данных из текста расписания
def extract_data_from_text(text):
    data = []
    lines = text.split("\n")
    classroom = ""
    teacher_full = ""

    for line in lines:
        if config.groop in line:
            # Извлекаем ФИО преподавателя
            parts = line.split()
            if len(parts) > 3:
                teacher_full = " ".join(parts[0:3])
            continue

        if teacher_full and "ауд." in line:
            # Извлекаем номер аудитории
            parts = line.split()
            if len(parts) > 1:
                classroom = parts[1]
            else:
                classroom = ""

            data.append({'teacher': teacher_full, 'classroom': classroom})
            teacher_full = ""

    return data

# Обработчик команды /rasp
def rasp_command(update, context):
    url = 'http://www.fa.ru/org/spo/kip/Documents/raspisanie/%d0%90%d1%83%d0%94%d0%98%d0%a2%d0%9e%d0%a0%d0%98%d0%98.pdf'
    response = requests.get(url)

    with io.BytesIO(response.content) as open_pdf_file:
        reader = PdfReader(open_pdf_file)
        data = []

        for page in reader.pages:
            text = page.extract_text()
            extracted_data = extract_data_from_text(text)
            if extracted_data:
                data.extend(extracted_data)

        if data:
            message = f"🔎 Найдены следующие данные для группы {config.groop}:"
            for entry in data:
                message += f"\n 🔖 Ауд. {entry['classroom']} {entry['teacher']}"
        else:
            message = f"🔎 Данные для группы {config.groop} не найдены"

    update.message.reply_text(message)

# Основная функция для запуска бота
def main():
    updater = Updater(config.token, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("rasp", rasp_command))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()