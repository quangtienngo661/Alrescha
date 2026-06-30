import requests
import os
from dotenv import load_dotenv
from helpers.Logger import logger

load_dotenv()

# class Article:
#     def __init__(self, id, title, body, html_url, updated_at):
#         self.id = id
#         self.title = title
#         self.body = body
#         self.html_url = html_url
#         self.updated_at = updated_at

def get_articles(per_page: int = 30):
    base_url = os.getenv("BASE_URL", "https://api.example.com/articles") 
    url = f"{base_url}?per_page={per_page}"  

    response = requests.get(url)

    if response.status_code == 200:
        articles_data = response.json().get("articles", [])
        return articles_data
    else:
        logger.error(f"[Fetcher] Failed to retrieve articles — HTTP {response.status_code}")
        return []
