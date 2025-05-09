import os
import time
import requests
from bs4 import BeautifulSoup

# Define diseases
diseases = ["anxiety", "diabetes", "asthma", "depression", "migraine"]

# API URLs: from pubmed.com
search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

output_dir = "pubmed_summaries"
os.makedirs(output_dir, exist_ok=True)

REQUEST_DELAY = 0.5  # seconds

for disease in diseases:
    print(f"\Processing disease: {disease}")

    # Get list of UIDs (max 20)
    search_params = {
        "db": "pubmed",
        "term": disease,
        "retmax": 20
    }
    search_response = requests.get(search_url, params=search_params)
    search_soup = BeautifulSoup(search_response.text, "xml")
    id_list = [id_tag.text for id_tag in search_soup.find_all("Id")]

    abstracts = []

    # Fetch data for each UID
    for uid in id_list:
        fetch_params = {
            "db": "pubmed",
            "id": uid,
            "retmode": "xml"
        }
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_soup = BeautifulSoup(fetch_response.text, "xml")

        # Extract all <AbstractText> sections
        abstract_tags = fetch_soup.find_all("AbstractText")
        abstract_text = "\n".join(tag.get_text(strip=True) for tag in abstract_tags)

        if abstract_text:
            abstracts.append(abstract_text)
        else:
            print(f"No abstract for UID {uid}")

        time.sleep(REQUEST_DELAY)

    # Save abstracts to file
    file_path = os.path.join(output_dir, f"{disease}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        for abstract in abstracts:
            f.write(abstract + "\n\n")

    print(f"Saved {len(abstracts)} abstracts for '{disease}' to '{file_path}'")
