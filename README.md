# hw05_final - Проект спринта: подписки на авторов, спринт 6 в Яндекс.Практикум

## Спринт 6 - Проект спринта: подписки на авторов

Проект социальной сети Yatube в рамках обучения на Python Backend Developer в Яндекс.Практикуме.
В рамках последнего спринта - создание функционала подписок, комментариев, тестирование.

Стек:

- Python 3.7.9
- Django==2.2.16
- mixer==7.1.2
- Pillow==8.3.1
- pytest==6.2.4
- pytest-django==4.4.0
- pytest-pythonpath==0.7.3
- requests==2.26.0
- six==1.16.0
- sorl-thumbnail==12.7.0
- Faker==12.0.1


### Настройка и запуск на ПК

Переходим в папку с проектом:

```bash
cd hw05_final
```

Устанавливаем виртуальное окружение:

```bash
python -m venv venv
```

Активируем виртуальное окружение:

```bash
source venv/Scripts/activate
```

> Для деактивации виртуального окружения выполним (после работы):
> ```bash
> deactivate
> ```

Устанавливаем зависимости:

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Применяем миграции:

```bash
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Создаем супер пользователя:

```bash
python yatube/manage.py createsuperuser


Запускаем проект:

```bash
python yatube/manage.py runserver
```

После чего проект будет доступен по адресу http://localhost:8000/

Заходим в http://localhost:8000/admin и создаем группы и записи.
После чего записи и группы появятся на главной странице.