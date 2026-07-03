import os
import glob
import json
from datetime import datetime

def parse_cleaned_content(lines):
    # Core Metrics Extraction
    nav_date = "Unknown"
    nav_val = "Unknown"
    min_sip = "Unknown"
    fund_size = "Unknown"
    expense_ratio = "Unknown"
    risk_category = "Unknown"
    
    # Try to grab risk category (it usually appears within the first 10 lines, e.g. "High Risk" or "Very High Risk")
    for i in range(min(20, len(lines))):
        if "Risk" in lines[i]:
            risk_category = lines[i]
            break

    for i, line in enumerate(lines):
        if line.startswith("NAV:"):
            nav_date = line.replace("NAV:", "").strip()
            if i + 1 < len(lines):
                nav_val = lines[i+1]
        elif line == "Min. for SIP":
            if i + 1 < len(lines):
                min_sip = lines[i+1]
        elif line == "Fund size (AUM)":
            if i + 1 < len(lines):
                fund_size = lines[i+1]
        elif line == "Expense ratio" and "fee payable" not in lines[i+1]:
            if i + 1 < len(lines):
                expense_ratio = lines[i+1]
                
    key_facts_text = f"NAV ({nav_date}): {nav_val}. Expense ratio: {expense_ratio}. Minimum SIP investment: {min_sip}. Fund size (AUM): {fund_size}. Riskometer Category: {risk_category}."
    
    # Section Extraction
    exit_load_text = ""
    benchmark_text = ""
    objective_text = ""
    tax_text = ""
    fund_mgr_text = ""
    
    for i, line in enumerate(lines):
        if line == "Investment Objective":
            if i + 1 < len(lines):
                objective_text = lines[i+1]
        
        elif line == "Fund benchmark":
            if i + 1 < len(lines):
                benchmark_text = f"Fund benchmark: {lines[i+1]}"
                
        elif line == "Exit Load":
            # Just grab the rule sentence (e.g. "Exit load of 1%, if redeemed within 15 days.")
            for j in range(i+1, min(i+10, len(lines))):
                if "Exit load of" in lines[j] or "if redeemed" in lines[j]:
                    exit_load_text = lines[j]
                    break
                    
        elif line == "Tax implication":
            if i + 1 < len(lines):
                tax_text = f"Stamp duty and tax implication: {lines[i+1]}"
                
        elif line == "Fund management":
            # Extract Manager Name, Education, and Experience
            mgr_name = lines[i+2] if i+2 < len(lines) else ""
            edu = ""
            exp = ""
            for j in range(i, min(i+15, len(lines))):
                if lines[j] == "Education" and j+1 < len(lines):
                    edu = lines[j+1]
                elif lines[j] == "Experience" and j+1 < len(lines):
                    exp = lines[j+1]
            fund_mgr_text = f"Fund Manager: {mgr_name}. Education: {edu}. Experience: {exp}"

    text_blocks = []
    text_blocks.append({"section_title": "Key fund facts", "text": key_facts_text})
    if exit_load_text:
        text_blocks.append({"section_title": "Exit load", "text": exit_load_text})
    if benchmark_text:
        text_blocks.append({"section_title": "Benchmark", "text": benchmark_text})
    if objective_text:
        text_blocks.append({"section_title": "Investment objective", "text": objective_text})
    if tax_text:
        text_blocks.append({"section_title": "Stamp duty and tax", "text": tax_text})
    if fund_mgr_text:
        text_blocks.append({"section_title": "Fund management", "text": fund_mgr_text})
        
    return nav_date, text_blocks

def main():
    os.makedirs("data/parsed", exist_ok=True)
    json_files = glob.glob("data/*.json")
    
    fetched_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+00:00")
    
    for filepath in json_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        fund_name = data.get("fund_name", "")
        source_url = data.get("source_url", "")
        cleaned_content = data.get("cleaned_content", "")
        lines = cleaned_content.split('\n')
        
        # Generate slug/id
        slug = os.path.basename(filepath).replace('.json', '')
        
        # Format id exactly as user screenshot (e.g. "hdfc-gold-etf-fund-of-fund-direct-plan-growth" -> "gold_fof" logic is tricky for all, we will just use the slug, but let's try to map if it's the gold one)
        scheme_id = slug
        if slug == "hdfc-gold-etf-fund-of-fund-direct-plan-growth":
            scheme_id = "gold_fof"
        elif slug == "hdfc-silver-etf-fof-direct-growth":
            scheme_id = "silver_fof"
            
        nav_date, text_blocks = parse_cleaned_content(lines)
        
        # Prepend the fund name into the text of the key fund facts to ensure context isn't lost
        if len(text_blocks) > 0 and text_blocks[0]["section_title"] == "Key fund facts":
             text_blocks[0]["text"] = f"{fund_name} key fund facts. " + text_blocks[0]["text"]
        
        parsed_data = {
            "scheme_id": scheme_id,
            "scheme_name": fund_name,
            "source_url": source_url,
            "nav_date": nav_date,
            "fetched_at": fetched_timestamp,
            "text_block_count": len(text_blocks),
            "text_blocks": text_blocks
        }
        
        output_path = os.path.join("data/parsed", f"{scheme_id}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)
            
        print(f"-> Parsed {slug} into {len(text_blocks)} semantic blocks.")

if __name__ == "__main__":
    main()
