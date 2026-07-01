import os
from helpers.Logger import logger
from openai import OpenAI
from uploader.base import AIKnowledgeBase

class OpenAIVectorStore(AIKnowledgeBase):
    def __init__(self, api_key: str, vector_store_id: str,
                 chunk_size: int = 800, overlap: int = 400):
        super().__init__(chunk_size, overlap)
        self.client = OpenAI(api_key=api_key)
        self.vector_store_id = vector_store_id

    def list_uploaded_files(self) -> dict:
        result = {}
        for vs_file in self.client.vector_stores.files.list(
            vector_store_id=self.vector_store_id
        ):
            attrs = vs_file.attributes or {}
            slug = attrs.get("slug")
            if slug:
                result[slug] = {
                    "file_id": vs_file.id,
                    "hash": attrs.get("hash"),
                }
        return result

    def upload_file(self, article: dict):
        file_obj = self.client.files.create(
            file=(f"{article["slug"]}.md", article["content"].encode("utf-8")),
            purpose="assistants",
        )

        self.client.vector_stores.files.create(
            vector_store_id=self.vector_store_id,
            file_id=file_obj.id,
            attributes={
                "slug": article["slug"],
                "hash": article["hash"],
                "url": article["url"],
                "article_id": str(article["id"]),
            },
            chunking_strategy={
                "type": "static",
                "static": {
                    "max_chunk_size_tokens": self.chunk_size,
                    "chunk_overlap_tokens": self.overlap,
                },
            },
        )

        return file_obj

    def delete_file(self, file_id: str) -> None:
        self.client.vector_stores.files.delete(
            vector_store_id=self.vector_store_id,
            file_id=file_id,
        )
        self.client.files.delete(file_id)

    def detect_delta(self, articles: list) -> tuple[list, list, list]:
        existing = self.list_uploaded_files()
        added, updated, skipped = [], [], []

        for article in articles:
            slug = article["slug"]
            if slug not in existing:
                added.append(article)
            elif existing[slug]["hash"] != article["hash"]:
                updated.append({**article, "file_id": existing[slug]["file_id"]})
            else:
                skipped.append(article)

        # logger.info(f"[Upload] Detected {len(added)} new, {len(updated)} updated, and {len(skipped)} skipped articles.")

        return added, updated, skipped