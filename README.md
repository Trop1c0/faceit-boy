# FACEIT Verification Discord Bot

Discord бот для верификации FACEIT аккаунтов пользователей с отображением их статистики.

## 🎯 Возможности

- Отправка верификации пользователям в личные сообщения
- Поддержка 6 языков (английский, русский, украинский, польский, немецкий, турецкий)
- Отображение статистики игрока: уровень, ELO, K/D
- Интерактивные кнопки для перехода к верификации
- Красивые embed-карточки с аватаром и баннером

## 📋 Требования

- Python 3.8+
- Discord Bot Token
- FACEIT API Key

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Trop1c0/faceit-boy.git
cd faceit-boy
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка .env файла

Скопируйте `.env.example` в `.env` и заполните своими данными:

```bash
cp .env.example .env
nano .env
```

```env
DISCORD_TOKEN=ваш_токен_discord_бота
GUILD_ID=ваш_id_сервера
FACEIT_API_KEY=ваш_faceit_api_key
VERIFY_URL=https://www.faceitverif.ru/
```

### 4. Запуск бота

```bash
python bot.py
```

## 🐧 Установка на Ubuntu 20.04

### Подготовка системы

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### Установка бота

```bash
# Клонирование репозитория
git clone https://github.com/Trop1c0/faceit-boy.git
cd faceit-boy

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
nano .env
```

### Создание systemd сервиса

Создайте файл `/etc/systemd/system/faceit-bot.service`:

```bash
sudo nano /etc/systemd/system/faceit-bot.service
```

Содержимое:

```ini
[Unit]
Description=FACEIT Verification Discord Bot
After=network.target

[Service]
Type=simple
User=ваш_username
WorkingDirectory=/home/ваш_username/faceit-boy
Environment="PATH=/home/ваш_username/faceit-boy/venv/bin"
ExecStart=/home/ваш_username/faceit-boy/venv/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените `ваш_username` на ваше имя пользователя!

### Запуск сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl start faceit-bot
sudo systemctl enable faceit-bot
sudo systemctl status faceit-bot
```

### Управление ботом

```bash
# Остановить
sudo systemctl stop faceit-bot

# Перезапустить
sudo systemctl restart faceit-bot

# Посмотреть логи
sudo journalctl -u faceit-bot -f
```

## 🔧 Обновление бота

```bash
cd faceit-boy
git pull origin main

# Если используете systemd
sudo systemctl restart faceit-bot
```

## 📝 Использование

### Команды

- `/verif @пользователь` - Отправить верификацию пользователю в ЛС

### Процесс верификации

1. Администратор использует `/verif @пользователь`
2. Пользователь получает сообщение в ЛС с выбором языка
3. Пользователь выбирает язык и вводит свой FACEIT никнейм
4. Бот показывает карточку с статистикой и кнопкой верификации
5. Пользователь нажимает кнопку и переходит на сайт верификации

## 🔑 Получение токенов

### Discord Bot Token

1. Перейти на https://discord.com/developers/applications
2. Создать новое приложение → Bot
3. Скопировать токен
4. Включить Privileged Gateway Intents (Presence, Server Members, Message Content)

### FACEIT API Key

1. Перейти на https://developers.faceit.com
2. Войти в аккаунт FACEIT
3. Создать приложение
4. Скопировать Server-side API Key

### Guild ID

1. Включить режим разработчика в Discord (Настройки → Расширенные → Режим разработчика)
2. ПКМ на сервере → Копировать ID

## 📂 Структура проекта

```
faceit-boy/
├── bot.py              # Основной файл бота
├── requirements.txt    # Зависимости Python
├── .env.example        # Пример конфигурации
├── .gitignore         # Игнорируемые файлы
├── README.md          # Документация
└── assets/            # Ресурсы
    ├── banner.webp    # Баннер для embed
    └── logo.png       # Логотип
```

## 🛠️ Решение проблем

### Ошибка: ModuleNotFoundError

```bash
pip install -r requirements.txt
```

### Бот не отвечает на команды

1. Проверьте что бот онлайн в Discord
2. Убедитесь что GUILD_ID правильный
3. Проверьте права бота на сервере
4. Посмотрите логи для деталей

### У пользователя закрыты ЛС

Бот сообщит администратору, что не может отправить сообщение. Пользователь должен включить личные сообщения от участников сервера.

## 📄 Лицензия

MIT License

## 🤝 Поддержка

Если у вас возникли проблемы или вопросы, создайте Issue в репозитории.
