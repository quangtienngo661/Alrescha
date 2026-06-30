import json
import hashlib
import slugify
import markdownify as md
from helpers.Logger import logger
from helpers.LoggingFormat import info_logging
from pathlib import Path

from scraper.cleaner import clean_content


def markdownify_html(html_content: str) -> str:
    return md.markdownify(html_content, heading_style="ATX")


def generate_hash(content: str) -> str:
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content.encode('utf-8'))
    return sha256_hash.hexdigest()


def generate_data(articles: list) -> list:
    data = []

    folder_path = "data"
    Path(folder_path).mkdir(exist_ok=True)

    json_file_path = Path(folder_path) / "json_files" / "articles.json"
    json_file_path.parent.mkdir(parents=True, exist_ok=True)

    md_folder_path = Path(folder_path) / "markdown_files"
    md_folder_path.mkdir(exist_ok=True)

    for article in articles:
        cleaned_content = clean_content(markdownify_html(article["body"]))

        article_data = {
            "id": article["id"],
            "url": article["html_url"],
            "title": article["title"],
            "slug": slugify.slugify(article["title"]),
            "content": cleaned_content,
            "hash": generate_hash(cleaned_content),
            "updated_at": article["updated_at"],
        }

        header = (
            f"---\n"
            f"Article Url: {article_data['url']}\n"
            f"ID: {article_data['id']}\n"
            f"title: \"{article_data['title']}\"\n"
            f"Updated Date: {article_data['updated_at']}\n"
            f"Hash: {article_data['hash']}\n"
            f"---\n\n"
        )
        article_data["content"] = header + article_data["content"]

        md_file_path = md_folder_path / f"{article_data['slug']}.md"
        with open(md_file_path, "w", encoding="utf-8") as f:
            f.write(article_data["content"])

        data.append(article_data)

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    logger.info(info_logging("Scraper", f"{len(data)} articles saved -> {md_folder_path}/"))
    return data
