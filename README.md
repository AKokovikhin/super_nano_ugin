# Nano Ugin v2

Django-приложение для управления оборудованием с REST API и Docker-развертыванием.

## Возможности

- Управление оборудованием и типами устройств
- REST API для интеграции
- Аутентификация пользователей
- Админ-панель Django
- Docker контейнеризация
- Автоматическое развертывание
- Преднастроенные тестовые данные

# Как развернуть проект
1. Клонируем репозиторий
   ```
   git clone <url-репозитория>
   ```
   
## Установка в ручном режиме

1. Настраиваем окружение:
```
bash
cd nano_ugin
python -m venv myvenv
source myvenv/bin/activate  # Linux/MacOS
```

2. Устанвливаем зависимости:
```
bash
cd nano_ugin
pip install -r requirements.txt
```

### Локальная разработка

3. Применяем миграции:
```
bash
python manage.py migrate
```

4. Создаём суперпользователя:
```
bash
python manage.py createsuperuser
```

5. При необходимости настраиваем систему (создает тестовые данные):
```
bash
python setup_system.py
```

6. Запускаем сервер:
```
bash
python manage.py runserver
```

## Автоматическое развертывание (Docker)
Запускаем автоматический деплой на порту 4545:
```
bash
./deploy.sh
```

Или вручную:

Собираем и запускаем контейнеры:
```
bash
docker-compose up --build
```

Применяем миграции:
```
bash
docker-compose exec web python manage.py migrate
```

Настраиваем систему (создает тестовые данные):
```
bash
docker-compose exec web python setup_system.py
```

Собираем статические файлы:
```
bash
docker-compose exec web python manage.py collectstatic --noinput
```

## Структура проекта
```
├── nano_ugin
│   ├── accounts                    # Приложение аутентификации
│   │   ├── migrations
│   │   │   └── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── equipment                    # Приложение оборудования
│   │   ├── templates                # Шаблоны оборудования
│   │   │   └── equipment
│   │   ├── admin.py
│   │   ├── api_urls.py
│   │   ├── api_views.py             # REST API views
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── models.py                # Модели оборудования
│   │   ├── tests.py
│   │   ├── views.py
│   │   └── web_urls.py
│   ├── nano_ugin                    # Настройки проекта
│   │   ├── asgi.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── staticfiles                  # Статические файлы
│   ├── templates                    # Базовые шаблоны
│   │   ├── registration
│   │   │   └── login.html
│   │   └── base.html
│   ├── manage.py
│   └── setup_system.py              # Настройка системы и тестовых данных
├── static
│   ├── admin
│   │   └── css
│   │       ├── custom.css
│   │       └── hide_fields.css
│   └── css
│       └── custom.css 
├── deploy.sh                         # Скрипт автоматического развертывания
├── docker-compose.yml                # запуск контейнеров базы данных и веба контейнеров
├── Dockerfile                        # Конфигурация Docker
├── README.md    
└── requirements.txt                  # Зависимости Python

```

## Скрипты развертывания

deploy.sh - Автоматический скрипт развертывания который:
- Проверяет наличие Docker и Docker Compose
- Создает необходимые конфигурационные файлы
- Запускает контейнеры на порту 4545
- Настраивает базу данных и применяет миграции
- Создает администратора (admin/admin)
- Запускает setup_system.py для наполнения данными

Запуск:
```
bash
chmod +x deploy.sh
./deploy.sh

```
setup_system.py
Скрипт инициализации системы который создает:
- Пользователей и группы (admin/admin, user/user)
- Типы устройств (Коммутаторы, Камеры, WiFi точки)
- Параметры оборудования
- Модели устройств
- Тестовые устройства с заполненными параметрами

Запуск:
```
bash
python setup_system.py
```


## API Endpoints
/api/equipment/ - Список оборудования
/api/device-types/ - Типы устройств

Другие endpoints смотрите в equipment/api_urls.py

## Доступ к системе
После запуска setup_system.py или deploy.sh создаются пользователи:

admin / admin - Полный доступ (администратор)
user / user - Ограниченный доступ (обычный пользователь)
