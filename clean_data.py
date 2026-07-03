import os
import glob
import json
from bs4 import BeautifulSoup

def process_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'lxml')
    
    # 1. Extract the Title and Clean it
    raw_title = soup.title.string if soup.title else "Unknown Fund"
    # Typically Groww titles look like: "HDFC Small Cap Fund Direct Growth - NAV, Mutual Fund Performance & Portfolio"
    fund_name = raw_title.split('- NAV')[0].strip()
    
    # 2. Identify Source URL from filename
    filename = os.path.basename(filepath)
    slug = filename.replace('.html', '')
    source_url = f"https://groww.in/mutual-funds/{slug}"
    
    # 3. Target the main content wrapper (ignoring global navs/sidebars)
    main_content = soup.find('div', class_='pw14ContentWrapper')
    if not main_content:
        # Fallback if the class differs
        main_content = soup.find('div', class_='layout-main')
    
    if not main_content:
        print(f"Warning: Could not find main content wrapper in {filename}. Falling back to full body.")
        main_content = soup.body if soup.body else soup

    # Remove generic hidden/script elements inside the wrapper
    for element in main_content(["script", "style", "svg", "button", "form", "noscript", "meta"]):
        element.decompose()
        
    # 4. Extract and Clean Text
    text = main_content.get_text(separator='\n', strip=True)
    
    # Collapse multiple newlines into a single newline
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)
            
    cleaned_text = '\n'.join(cleaned_lines)
    
    return {
        "fund_name": fund_name,
        "source_url": source_url,
        "cleaned_content": cleaned_text
    }

def main():
    os.makedirs("data", exist_ok=True)
    
    html_files = glob.glob("raw_data/*.html")
    for filepath in html_files:
        print(f"Cleaning {filepath}...")
        
        try:
            data_dict = process_html_file(filepath)
            
            # Write to JSON
            slug = os.path.basename(filepath).replace('.html', '')
            output_path = os.path.join("data", f"{slug}.json")
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=4, ensure_ascii=False)
                
            print(f"  -> Saved clean JSON to {output_path}")
            
        except Exception as e:
            print(f"  -> Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()
