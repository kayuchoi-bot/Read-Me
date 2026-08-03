import os
import xml.etree.ElementTree as ET
import urllib.parse
import requests
from google import genai

# 1. Load Secrets
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Fetch Latest News via Google News RSS Feed
def fetch_tsui_wah_news():
    query = urllib.parse.quote('"Tsui Wah" OR "翠華" OR "翠華餐廳"')
    # Fetch HK/EN coverage
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(rss_url, headers=headers, timeout=10)
    root = ET.fromstring(response.content)
    
    articles = []
    for item in root.findall(".//item")[:10]:  # Pull top 10 relevant news items
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        articles.append(f"- {title}\n  Link: {link}")
        
    return "\n".join(articles) if articles else "No news found today."

# 3. AI Intelligence Layer (Gemini)
def generate_ai_summary(news_data):
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    You are a market intelligence agent. Summarize the following news items about Tsui Wah (翠華餐廳) into a daily digest.
    Categorize into Business/Financial, Food/Operations, or General Sentiment if applicable.
    Format cleanly with bullet points in Markdown for Telegram. Keep it brief and executive.
    
    News items:
    {news_data}
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    return response.text

# 4. Telegram Delivery
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=10)

if __name__ == "__main__":
    raw_news = fetch_tsui_wah_news()
    summary = generate_ai_summary(raw_news)
    send_telegram_message(f"🍜 *Tsui Wah Daily News Digest*\n\n{summary}")
