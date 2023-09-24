import subprocess
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = "ВАШ ТОКЕН БОТА"
CORP_CERTIFICATE_PATH = "ПУТЬ НА .p12"
CORP_CERTIFICATE_PASSWORD = "ПАРОЛЬ СЕРТИФИКАТА"
BUNDLE_IDENTIFIER = "BUNDLE"
#APP_TITLE = "ИМЯ ФАЙЛА ДЭФОЛТ УСТАНОВКА"
#APP_VERSION = "ВЕРСИЯЯ"
BASE_URL = "https://ВАШАССЫЛКА/"

def start(update: Update, context):
    update.message.reply_text("Привет! Отправьте ipa-файл для подписи.")

def sign_ipa(update: Update, context):
    # Проверка наличия ipa-файла
    if not update.message.document:
        update.message.reply_text("Пожалуйста, отправьте ipa-файл.")
        return

    # Получение файла ipa
    ipa_file = context.bot.get_file(update.message.document.file_id)
    ipa_file.download("app.ipa")

    # Подписание ipa с использованием zsign
    command = f"zsign -k {CORP_CERTIFICATE_PATH} -p {CORP_CERTIFICATE_PASSWORD} -m {BUNDLE_IDENTIFIER} -o signed_app.ipa app.ipa"
    subprocess.run(command, shell=True, check=True)

    # Генерация plist
    plist_content = generate_plist()

    # Сохранение plist на сервере
    plist_filename = "app.plist"
    plist_filepath = os.path.join("path_to_save_plist", plist_filename)
    with open(plist_filepath, "w") as plist_file:
        plist_file.write(plist_content)

    # Отправка подписанного ipa и ссылки на plist пользователю
    signed_ipa_file = open("signed_app.ipa", "rb")
    plist_url = f"{BASE_URL}{plist_filename}"
    message_text = f"Ссылка на установку: {plist_url}"
    context.bot.send_document(chat_id=update.message.chat_id, document=signed_ipa_file)
    context.bot.send_message(chat_id=update.message.chat_id, text=message_text)

def generate_plist():
    plist_content = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>items</key>
        <array>
            <dict>
                <key>assets</key>
                <array>
                    <dict>
                        <key>kind</key>
                        <string>software-package</string>
                        <key>url</key>
                        <string>{BASE_URL}signed_app.ipa</string>
                    </dict>
                </array>
                <key>metadata</key>
                <dict>
                    <key>bundle-identifier</key>
                    <string>{BUNDLE_IDENTIFIER}</string>
                    <key>bundle-version</key>
                    <string>{APP_VERSION}</string>
                    <key>kind</key>
                    <string>software</string>
                    <key>title</key>
                    <string>{APP_TITLE}</string>
                </dict>
            </dict>
        </array>
    </dict>
    </plist>
    """

    return plist_content

def main():
    # Инициализация бота
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Добавление обработчиков команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, sign_ipa))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
