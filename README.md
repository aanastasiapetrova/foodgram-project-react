***Foodgram*** - сервис для публикации рецептов, где пользователи могут добавлять особенно понравившиеся рецепты в раздел "Избранное", формировать и скачивать список покупок и подписываться на авторов со схожими вкусами.

## Запуск проекта
### Склонируйте репозиторий:
```
git clone git@github.com:aanastasiapetrova/foodgram-project-react.git
```
* Подключитесь к удаленному серверу

* Установите **docker** и **docker-compose** на сервер:
```
sudo apt install docker.io 
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
* В файле конфигурации сервера **nginx** *infra/nginx.conf*  в строке server_name впишите свой IP

* Cоздайте .env файл и впишите:
    ```
    SECRET_KEY = <секретный ключ из backend/settings.py>
    POSTGRES_USER = <имя пользователя базы данных> 
    POSTGRES_PASSWORD = <пароль для доступа к базе данных>
    POSTGRES_DB = <название базы данных>
    DB_ENGINE="django.db.backends.postgresql"
    DB_PORT=5432
    DB_HOST="db"
    ```
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
    ```
    SECRET_KEY = <секретный ключ из backend/settings.py>
    POSTGRES_USER = <имя пользователя базы данных> 
    POSTGRES_PASSWORD = <пароль для доступа к базе данных>
    POSTGRES_DB = <название базы данных>
    DB_ENGINE="django.db.backends.postgresql"
    DB_PORT=5432
    DB_HOST="db"
    
    DOCKER_LOGIN=<имя пользователя DockerHub>
    DOCKER_PASSWORD=<пароль от DockerHub>
    
    USER = <username для подключения к серверу>
    HOST = <IP сервера>
    PASSPHRASE = <пароль для сервера, если он установлен>
    SSH_KEY = <SSH ключ>

    TELEGRAM_TO = <ID пользователя Telegram>
    BOT_TOKEN = <токен вашего бота>
    ```
  
* Для запуска проекта на сервере необходимо выполнить команду:
```
sudo docker-compose up -d
```
* При первом запуске проекта выполните следующие действия:
    - Соберите статические файлы:
    ```
    sudo docker compose exec backend python manage.py collectstatic
    ```
    ```
    cp -r backend/collected_static/. ../backend_static/static/
    
    ```
    - Примените миграции:
    ```
    sudo docker compose exec backend python manage.py migrate 
    ```
    - Создайте суперпользователя для роботы в административном интерфейсе:
    ```
    sudo docker compose exec backend python manage.py 
    createsuperuser
    ```
    - Загрузите ингридиенты в базу данных:  
    ```
    sudo docker-compose exec backend python manage.py import
    ```
    - Проект находится по адресу http://<IP адрес удаленного сервера>/recipes

## Проект в интернете
Проект запущен и доступен по http://51.250.102.44/recipes
(Админка: login - admin, password - admin)