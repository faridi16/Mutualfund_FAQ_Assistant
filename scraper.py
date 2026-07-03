import os
import requests
from bs4 import BeautifulSoup

URLS = [
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Remove boilerplate elements that don't contain fund facts
    for element in soup(["script", "style", "nav", "footer", "header", "svg", "button", "form", "noscript", "meta"]):
        element.decompose()
        
    # Attempt to extract title/name
    title = soup.title.string if soup.title else "Unknown Fund"
    
    # Extract text with a newline separator to keep layout spacing (like tables) somewhat intact
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up excessive newlines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)
            
    # Rejoin with a newline
    return title, '\n'.join(cleaned_lines)

def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("raw_data", exist_ok=True)
    
    for url in URLS:
        slug = url.strip('/').split('/')[-1]
        print(f"Fetching {slug}...")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            # Save raw HTML for review
            raw_output_path = os.path.join("raw_data", f"{slug}.html")
            with open(raw_output_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Clean and save text
            title, text = clean_html(response.text)
            output_content = f"Source URL: {url}\nTitle: {title}\n\n{text}"
            
            output_path = os.path.join("data", f"{slug}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output_content)
                
            print(f"  -> Saved HTML to {raw_output_path}")
            print(f"  -> Saved Cleaned Text to {output_path}")
            
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")

if __name__ == "__main__":
    main()
