import requests
from bs4 import BeautifulSoup
from config import ACCOUNT_SID, AUTH_TOKEN, FROM_WHATSAPP_NUMBER, TO_WHATSAPP_NUMBER
from twilio.rest import Client


def fetch_top_10_news():
    url = "https://thehackernews.com/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    article_links = soup.find_all("a", class_="story-link")

    top_news = []
    for link_tag in article_links[:10]:
        title_tag = link_tag.find("h2", class_="home-title") or link_tag.find("div", class_="home-title")
        title = title_tag.text.strip() if title_tag else "No Title"
        link = link_tag['href'].strip() if link_tag.has_attr("href") else "No Link"
        top_news.append(f"• {title}\n🔗 {link}")

    return top_news


def filter_new(news_list):
    try:
        with open("seen_articles.txt", "r", encoding="utf-8") as f:
            seen = f.read().splitlines()
    except FileNotFoundError:
        seen = []

    new_items = [item for item in news_list if item.split("\n")[1] not in seen]

    with open("seen_articles.txt", "a", encoding="utf-8") as f:
        for item in new_items:
            f.write(item.split("\n")[1] + "\n")

    return new_items



def send_whatsapp_message(body):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages.create(
        from_=FROM_WHATSAPP_NUMBER,
        body=body,
        to=TO_WHATSAPP_NUMBER
    )
    print("✅ WhatsApp Message Sent | SID:", message.sid)


if __name__ == "__main__":
    top_news = fetch_top_10_news()
    new_items = filter_new(top_news)

    if new_items:
        message_text = "🛡️ *Top 10 Cybersecurity News Today*\n\n" + "\n\n".join(new_items)
        send_whatsapp_message(message_text[:1600])  # Twilio message limit
    else:
        print("ℹ️ No new news to send today.")
