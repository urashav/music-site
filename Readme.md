#Deploy

Клонируем в папку с проектом <project_name>
git clone https://github.com/urashav/music-site.git ./<project_name>

Устанавливаем окружение (проверить версию интерпретатора)
pipenv install --ignore-pipfile

Заливаем файлы настроек сервера в КОРЕНЬ папки с проектом
scp -r srv_config/<project_name>/* msc-s1:~/www/<project_name>/

