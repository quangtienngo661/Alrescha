import os
from dotenv import load_dotenv
from openai import OpenAI, NotFoundError
from helpers.Logger import logger

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID")

def init_vector_store(name: str = "Alrescha"):
    vector_store = None

    if vector_store_id:
        try:
            vector_store = client.vector_stores.retrieve(vector_store_id=vector_store_id)
            logger.info(f"[VectorStore] Reusing existing store: {vector_store.id}")
        except NotFoundError:
            logger.warning(f"[VectorStore] ID '{vector_store_id}' not found on OpenAI. Creating new...")
        except Exception as e:
            logger.error(f"[VectorStore] Error validating store: {e}")

    if not vector_store:
        try:
            store_lists = client.vector_stores.list()
            if len(store_lists.data) > 0:
                logger.warning(f"[VectorStore] Existing stores found. Please set OPENAI_VECTOR_STORE_ID in .env to one of the following:")
                for vs in store_lists.data:
                    logger.info(f"{vs.id} (name: {vs.name})")
                return None
            vector_store = client.vector_stores.create(name=name)
            logger.info(f"[VectorStore] New store created: {vector_store.id}")
            logger.info(f"[VectorStore] Add to .env: OPENAI_VECTOR_STORE_ID={vector_store.id}")
            return None
        except Exception as e:
            logger.error(f"[VectorStore] Failed to create store: {e}")
    
    return vector_store

