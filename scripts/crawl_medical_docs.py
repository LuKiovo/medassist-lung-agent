import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from medassist_lung_agent.config import settings
from medassist_lung_agent.rag.crawler import save_url_as_txt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="append", required=True, help="Trusted medical page URL")
    args = parser.parse_args()
    for url in args.url:
        path = save_url_as_txt(url, settings.rag_doc_dir)
        print(f"Saved {url} -> {path}")


if __name__ == "__main__":
    main()
