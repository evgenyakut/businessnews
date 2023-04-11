import openai
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd

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
    # telebot(df, 'Noticias del portal Expansion')
    return df.title.head(10)


df = parsing_exp()
# Формируем сообщение

prompt = "Переведи заголовки на русский, оставляя названия компаний в оригинале: {}\n".format(list(df))

# Замените YOUR_API_KEY на ваш действительный API-ключ
openai.api_key = "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"

# Параметры запроса
engine = "gpt-3.5-turbo"  # Используется предполагаемый движок GPT-3.5-turbo
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}
]

max_tokens = 1000
temperature = 0.5

# Отправка запроса к API 
response = openai.ChatCompletion.create(
    model=engine,
    messages=messages,
    max_tokens=max_tokens,
    temperature=temperature
)

if response is not None:
    generated_text = response.choices[0].message.content
    print("Сгенерированный текст:", generated_text.strip())
else:
    print("Ошибка при выполнении запроса.")