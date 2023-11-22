import time
import requests
import os
import smtplib
from email.message import EmailMessage
import zipfile
import logging

# Функция для отправки email-уведомлений
def send_email_notification(subject, body, sender_email, sender_password, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(sender_email, sender_password)
    s.send_message(msg)
    s.quit()

# Функция для создания резервной копии
def create_backup(src_folder, dest_folder):
    try:
        backup_name = time.strftime("%Y-%m-%d_%H-%M-%S")
        backup_folder = os.path.join(dest_folder, backup_name)
        with zipfile.ZipFile(backup_folder + '.zip', 'w') as zipf:
            for root, dirs, files in os.walk(src_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), src_folder))
        logging.info(f'Резервная копия {backup_name}.zip создана успешно.')
        return backup_folder + '.zip'
    except Exception as e:
        logging.error(f'Ошибка при создании резервной копии: {e}')
        return None

# Функция для загрузки резервной копии на Яндекс.Диск
def upload_to_yandex_disk(file_path, yandex_disk_url, token):
    try:
        with open(file_path, 'rb') as f:
            response = requests.put(yandex_disk_url, headers={'Authorization': 'OAuth ' + token}, files={'file': f})
        if response.status_code == 201:
            logging.info('Резервная копия загружена на Яндекс Диск.')
        else:
            logging.error('Ошибка загрузки резервной копии на Яндекс Диск.')
    except Exception as e:
        logging.error(f'Ошибка при загрузке на Яндекс Диск: {e}')

def main():
    src_folder = input('Введите путь к папке, которую хотите скопировать:\n')
    dest_folder = input('Введите путь к папке, в которую хотите сохранять резервные копии:\n')
    yandex_disk_url = input('Введите ссылку к папке на Яндекс Диске, в которую хотите сохранять резервные копии:\n')
    token = input('Введите токен доступа:\n')

    backup_interval = int(input('Введите интервал выполнения в минутах:\n'))  # Пользователь вводит интервал

    sender_email = input('Введите ваш Email адрес для отправки уведомлений:\n')
    sender_password = input('Введите пароль от вашего Email адреса:\n')
    to_email = input('Введите Email адрес для уведомлений:\n')

    # Настройка журнала для регистрации событий
    logging.basicConfig(filename='backup_log.log', level=logging.INFO
                        , format='%(asctime)s - %(levelname)s: %(message)s')

    while True:
        try:
            # Создание резервной копии и выполнение действий по успешному или неуспешному завершению
            backup_file = create_backup(src_folder, dest_folder)
            if backup_file:
                upload_to_yandex_disk(backup_file, yandex_disk_url, token)
                os.remove(backup_file)  # Удаляем локальный файл после загрузки на Яндекс Диск
            send_email_notification('Успешное резервное копирование'
                                    , 'Резервное копирование выполнено успешно'
                                    , sender_email, sender_password, to_email)
            # Обработка исключений и отправка уведомлений в случае возникновения ошибок
        except Exception as e:
            logging.error(f'Исключение: {e}')
            send_email_notification('Ошибка при резервном копировании', f'Произошла ошибка: {e}'
                                    , sender_email, sender_password, to_email)
        time.sleep(backup_interval * 60)

if __name__ == "__main__":
    main()

