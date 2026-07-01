from helpers.Logger import logger
from uploader.base import AIKnowledgeBase

def estimated_chunk_count(openai_instance: AIKnowledgeBase, content: str) -> int:
    chunk_size = openai_instance.chunk_size
    overlap = openai_instance.overlap

    estimated_tokens = len(content) / 4

    if estimated_tokens <= chunk_size:
        return 1

    chunks = 1 + (estimated_tokens - chunk_size) / (chunk_size - overlap)
    return int(chunks)

def upload_articles(openai_instance: AIKnowledgeBase, articles: list):
    count = 0
    failed = 0
    total_chunks = 0

    added, updated, skipped = openai_instance.detect_delta(articles)
    
    if len(added) > 0:
        logger.info(f"[Upload] {len(added)} new articles to upload.")

        for article in added:
            try:
                openai_instance.upload_file(article)
                chunks = estimated_chunk_count(openai_instance, article["content"])
                count += 1
                total_chunks += chunks
                logger.info(f"[Upload] {article['slug']} (~{chunks} chunks) ✓")
            except Exception as e:
                failed += 1
                logger.error(f"[Upload] Failed '{article['slug']}': {e}")
                continue

    if len(updated) > 0:
        logger.info(f"[Upload] {len(updated)} updated articles to upload.")

        for article in updated:
            try:
                openai_instance.delete_file(article["file_id"])
                openai_instance.upload_file(article)
                chunks = estimated_chunk_count(openai_instance, article["content"])
                count += 1
                total_chunks += chunks
                logger.info(f"[Upload] {article['slug']} (~{chunks} chunks) ✓")
            except Exception as e:
                failed += 1
                logger.error(f"[Upload] Failed '{article['slug']}': {e}")
                continue

    logger.info("===============================================================")
    openai_instance.log_summary(added, updated, skipped)
    logger.info(f"[Upload] Total articles uploaded: {count} | Failed: {failed}")
    logger.info(f"[Upload] Total chunks processed (estimated): {total_chunks}")

