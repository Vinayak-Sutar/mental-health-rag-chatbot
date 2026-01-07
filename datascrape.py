import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- CONFIGURATION ---
BASE_URL = "https://www.nimh.nih.gov"
START_URL = "https://www.nimh.nih.gov/health/publications"
OUTPUT_DIR = "nimh_text_data"

# Headers to mimic a real browser (prevents blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_soup(url):
    """Fetches a page and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"  [Error] Failed to load {url}: {e}")
        return None

def clean_text(text):
    """Cleans up whitespace and newlines."""
    if not text: return ""
    return " ".join(text.split())

def save_to_txt(topic, title, content, url):
    """Saves the scraped content to a text file."""
    # Create a safe filename
    safe_title = "".join([c if c.isalnum() else "_" for c in title])[:50] 
    safe_topic = "".join([c if c.isalnum() else "_" for c in topic])[:30]
    filename = f"{safe_topic}-{safe_title}.txt"
    
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"TOPIC: {topic}\n")
        f.write(f"TITLE: {title}\n")
        f.write(f"SOURCE_URL: {url}\n")
        f.write("-" * 40 + "\n\n")
        f.write(content)
    
    print(f"  [Saved] {filename}")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"--- Starting Scrape from {START_URL} ---")
    soup = get_soup(START_URL)
    if not soup: return

    # 1. FIND TOPIC LINKS (Level 1)
    # Looking for links like: /health/publications/anxiety-disorders-listing
    topic_links = set()
    
    # We target the main area to avoid footer/nav links
    main_content = soup.find("main") or soup.find("div", role="main")
    
    if main_content:
        for a in main_content.find_all("a", href=True):
            href = a['href']
            # Logic: Must be in publications, not be a PDF, and usually implies a listing
            if "/health/publications/" in href and not href.endswith(".pdf"):
                # Exclude simple pagination or sorting links if any
                if "listing" in href or href.count("/") == 3: # broad check for category pages
                    full_url = urljoin(BASE_URL, href)
                    topic_links.add(full_url)

    print(f"Found {len(topic_links)} topics. Processing...")

    # 2. PROCESS EACH TOPIC (Level 2)
    for topic_url in topic_links:
        print(f"\n[Topic Page] {topic_url}")
        topic_soup = get_soup(topic_url)
        if not topic_soup: continue

        # Extract Topic Name
        topic_name_tag = topic_soup.find("h1")
        topic_name = topic_name_tag.get_text(strip=True) if topic_name_tag else "Unknown_Topic"

        # Find Article Links inside the topic page
        # Logic: Links that look like /health/publications/generalized-anxiety-disorder-gad
        article_links = set()
        topic_main = topic_soup.find("main") or topic_soup.find("div", role="main")

        if topic_main:
            for a in topic_main.find_all("a", href=True):
                href = a['href']
                full_url = urljoin(BASE_URL, href)

                # FILTERS:
                # 1. Must be in /publications/
                # 2. Must NOT be a PDF
                # 3. Must NOT be the topic page itself (listing)
                # 4. Must NOT be Spanish (/es/, espanol)
                if ("/health/publications/" in href 
                    and not href.endswith(".pdf") 
                    and "listing" not in href
                    and "/es/" not in href
                    and "espanol" not in href.lower()):
                    
                    # Ensure it's not just a hash link (anchor) on the same page
                    if full_url != topic_url:
                        article_links.add(full_url)

        # 3. PROCESS EACH ARTICLE (Level 3)
        for article_url in article_links:
            # Simple check to avoid scraping the main list again if logic slipped
            if article_url == topic_url: continue
            
            print(f"  -> Scraping Article: {article_url}")
            article_soup = get_soup(article_url)
            if not article_soup: continue

            # Extract Title
            title_tag = article_soup.find("h1")
            article_title = title_tag.get_text(strip=True) if title_tag else "No_Title"

            # Extract Main Content
            # NIMH usually puts the text in a 'div' with class 'node-content' or inside <main>
            content_area = article_soup.find("div", class_="node-content")
            if not content_area:
                 content_area = article_soup.find("main")

            if content_area:
                # Remove "En español" links and other clutter
                for junk in content_area.find_all(["div"], class_=["social-share", "callout", "toc"]):
                    junk.decompose()

                # Get text from paragraphs and list items only (cleanest approach)
                text_blocks = []
                for element in content_area.find_all(['p', 'li', 'h2', 'h3']):
                    text = element.get_text(strip=True)
                    if text and "En español" not in text:
                        text_blocks.append(text)
                
                full_text = "\n\n".join(text_blocks)
                
                if len(full_text) > 200: # Only save if we actually found substantial text
                    save_to_txt(topic_name, article_title, full_text, article_url)
            
            # Be polite to the server
            time.sleep(0.5)

    print(f"\n--- Job Complete. Check /{OUTPUT_DIR} ---")

if __name__ == "__main__":
    main()