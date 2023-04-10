import pandas as pd
import requests
from bs4 import BeautifulSoup
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from datetime import datetime, timedelta
import time
import schedule


def telebot(tbl, titl):
    # создание бота и установка токена
    bot = telegram.Bot(token='6239401958:AAHkXIvP_VMj-VVUmQw7F0wvVIfPM8KZPEM')

    # таблица с данными
    data = tbl.loc[:, ["title", "link"]].to_dict('records')

    # формирование текста сообщения
    message_text = f"{titl}\n\n"  # добавляем заголовок
    for item in data:
        # форматирование текста сообщения
        message_text += '{}\n<a href="{}">Leer articulo</a>\n\n'.format(item['title'], item['link'])


    # отправка сообщения ботом
    bot.send_message(chat_id='@businessnewspain', text=message_text, parse_mode=telegram.ParseMode.HTML)

# Парсинг Expansion

def parsing_exp():

    urls = ["https://www.expansion.com/juridico.html", 
            "https://www.expansion.com/empresas.html", 
            "https://www.expansion.com/economia.html",
            "https://www.expansion.com/fiscal.html"]

    articles = []

    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        for i, article in enumerate(soup.find_all("article")):
            if i >= 10:
                break
            h2 = article.find("h2")
            if h2:
                a = h2.find("a")
                if a:
                    article_url = a["href"] 
                    if "www.expansion.com" not in article_url:
                        continue
                    article_page = requests.get(article_url)
                    article_soup = BeautifulSoup(article_page.content, "html.parser")
                    time = article_soup.find("time")
                    if not time:
                        continue
                    time_str = time.get("datetime")
                    try:
                        dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                    except (ValueError, TypeError):
                        continue
                    articles.append({"title": h2.text.strip(),'link': article_url, "datetime": dt})

    # Get current date and subtract 1 days
    current_date = datetime.now()
    delta = timedelta(days=1)
    week_ago = current_date - delta

    # Filter articles by date
    filtered_articles = [a for a in articles if a["datetime"] > week_ago]
    df = pd.DataFrame(filtered_articles)
    telebot(df, 'Noticias del portal Expansion')
    return

# Парсинг Idealista

def parsing_idl():

    urls = ["https://www.idealista.com/news/finanzas",
            'https://www.idealista.com/news/inmobiliario',
            'https://www.idealista.com/news/fiscalidad',
            'https://www.idealista.com/news/deco']

    articles = []

    skip_urls = ['/news/inmobiliario/top-idealista']

    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        for i, article in enumerate(soup.find_all("article")):
            h2 = article.find("h2")
            if h2:
                a = h2.find("a")
                if a:
                    article_url = ("https://www.idealista.com"+a["href"])
                    if any(skip in article_url for skip in skip_urls):
                        continue
                    article_page = requests.get(article_url)
                    article_soup = BeautifulSoup(article_page.content, "html.parser")
                    time = article_soup.find("time")
                    if not time:
                        continue
                    time_str = time.get("datetime")
                    try:
                        dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
                    except (ValueError, TypeError):
                        continue
                    articles.append({"title": h2.text.strip(), "link": article_url, "datetime": dt})

    # Get current date and subtract 4 days
    current_date = datetime.now()
    delta = timedelta(days=4)
    week_ago = current_date - delta

    # Filter articles by date
    filtered_articles = [a for a in articles if a["datetime"] > week_ago]
    df = pd.DataFrame(filtered_articles)
    telebot(df, 'Noticias del portal Idealista')
    return

# настройка расписания
schedule.every().day.at('07:00').do(parsing_exp)
schedule.every(2).days.at('07:30').do(parsing_idl)

# бесконечный цикл для проверки расписания
while True:
    schedule.run_pending()
    time.sleep(1)

