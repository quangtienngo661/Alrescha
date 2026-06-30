import os
from scraper.fetcher import get_articles
from scraper.writer import generate_data
from init.setup_vector_store import init_vector_store
from uploader.bulk_upload import upload_articles
from uploader.openai_store import OpenAIVectorStore
from dotenv import load_dotenv
from helpers.Logger import logger

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    vector_store = init_vector_store()
    if vector_store:
        openai_instance = OpenAIVectorStore(
            api_key=api_key,
            vector_store_id=vector_store.id,  # ← dùng ID thật, không phải biến env cũ
            chunk_size=800,
            overlap=400
        )
        articles = get_articles(50)
        formated_articles = generate_data(articles)
        upload_articles(openai_instance, formated_articles)
    else:
        logger.error("No valid vector store available. Aborting.")
        exit(1)