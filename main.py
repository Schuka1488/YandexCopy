import time
import shutil
import urllib
from urllib.request import urlretrieve, Request

src_folder = input('Введите путь к папке, которую хотите скопировать:\n')
dest_folder = input('Введите путь к папке, в которую хотите сохранять резервные копии:\n')
yandex_disk_url = input('Введите ссылку к папке на Яндекс Диске, в которую хотите сохранять резервные копии:\n')
token = input('Введите токен доступа\n')

backup_interval = 1

while True:
    backup_name = time.strftime("%Y-%m-%d_%H-%M-%S")
    backup_folder = dest_folder + backup_name + "/"

    shutil.copytree(src_folder, backup_folder)
    print('Резервное копирование выполнено успешно.')

    headers = {'Authorization': 'OAuth' + token}
    params = {'path': backup_name, 'overwrite': 'true'}

    request = Request(yandex_disk_url, headers=headers, method='PUT')

    with urllib.request.urlopen(request) as f:
        html = f.read()
    if html and html.status_code == 201:
        print('Резервная копия загружена на Яндекс Диск.')
    else:
        print('Ошибка загрузки резервной копии на Яндекс Диск.')

    time.sleep(backup_interval * 60)
