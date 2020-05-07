# DRF-apps-test
Тестовое задание


### Задача
реализовать API, позволяющее добавлять, изменять, просматривать и удалять данные в модели "Приложения".
"Приложения" – это модель, которая хранит в себе внешние источники, которые будут обращаться к API. Обязательные поля модели: ID, Название приложения, Ключ API. Поле "Ключ API" нельзя менять через API напрямую, должен быть метод, позволяющий создать новый ключ API.
После добавления приложения – должна быть возможность использовать "Ключ API" созданного приложения для осуществления запросов к метод /api/test, метод должен возвращать JSON, содержащий всю информацию о приложении.


### Технологии
+ Django 2.2.7
+ Django REST framework


### Deploy

#### Debian-based OS

```bash
# getting src
git clone https://github.com/actechnologies/DRF-apps-test.git && cd DRF-apps-test

# setting venv
sudo apt install python3-venv -y
python3 -m venv ./venv
source venv/bin/activate

# install dependies
pip install --upgrade pip
pip install -r requirements.txt
sudo apt install nginx postgresql-10 -y

# setup database
echo "create database appsapi; create user appsapi with encrypted password 'passw0rd'; grant all privileges on database appsapi to appsapi;" | sudo -u postgres psql 
python manage.py makemigrations
python manage.py migrate

# change data for services configs
sed -i 's?{{work_dir}}?'`pwd`'?' configs/apps_api_gunicorn.service
sed -i 's?{{work_dir}}?'`pwd`'?' configs/apps_api_nginx.conf

# copy configs to destination
sudo chown www-data:www-data .
sudo cp configs/apps_api_nginx.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/apps_api_nginx.conf /etc/nginx/sites-enabled/
sudo cp configs/apps_api_gunicorn.service /etc/systemd/system/

# start services
sudo systemctl daemon-reload
python manage.py collectstatic --noinput
sudo systemctl start apps_api_gunicorn
sudo nginx -s reload
```

### How To
для простоты и ускорения не стал реализовывать дополнительную авторизацию для методов API, оставил модель управления доступом стандартную django, на саму логику работы приложения это не влияет для тестового варианта, при желании можно будет добавить любой удобный метод авторизации (JWT, например) всего в пару строк

проверить работу API можно через стандартный веб-интерфейс DRF

#### для проверки api:
* зарегистрируйте аккаунт админа в django:
```bash
python manage.py createsuperuser
```
* авторизуйтесь в админке
http://localhost/admin
* откройте ссылку с api
http://localhost/api/v1.0/apps/

#### работа с моделью apps
* создание

POST запрос на ```http://localhost/api/v1.0/apps/```

Обязательное поле **appname**

В ответ прилетает сгенерированный ключ API ```api_key```, он не хранится нигде и не может быть отправлен клиенту повторно, клиент самостоятельно хранит ключ и использует его в дальнейшем  

* просмотр (чтение)

GET запрос на ```http://localhost/api/v1.0/apps/<appname>```

* изменение 

PUT запрос на ```http://localhost/api/v1.0/apps/<appname>```

Обязательное поле **appname** (при PATCH можно отправлять любые поля формы, кроме ключа)

*  удаление

DELETE запрос на ```http://localhost/api/v1.0/apps/<appname>```

* сброс API ключа

POST запрос на  ```http://localhost/api/v1.0/apps/<appname>/new_key/```

В ответ прилетает сгенерированный ключ API ```api_key```, он не хранится нигде и не может быть отправлен клиенту повторно, клиент самостоятельно хранит ключ и использует его в дальнейшем

#### проверка API ключа приложения

GET запрос на ```http://localhost/api/test/```

**обязательный заголовок:**

"Authorization: Api-Key * * *"

в ответ прилетает информация по самому приложению, увеличивается счетчик количества запросов и отмечается время обращения (их можно изменить в самой модели)

проверка можно быть реализована с помощью команды:

```curl -H "Authorization: Api-Key <your_key>" http://localhost/api/test/```