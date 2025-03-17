import requests
from bs4 import BeautifulSoup
import re  # Import regex for cleaning price

def clean_price(price_text):
    """Cleans the price text by removing EMI and extra symbols."""
    if not price_text:
        return "Price Not Available"
    
    # Remove everything after "*" or "EMI"
    cleaned_price = re.split(r'\*|EMI', price_text)[0].strip()
    
    return cleaned_price

def variant_links(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    variants = {}

    for variant in soup.find_all('div', class_='variantCard shadow16 outervariant'):
        link_tag = variant.find('a', class_='link hover')
        price_tag = variant.find('div', class_='price')

        if link_tag and 'title' in link_tag.attrs and 'href' in link_tag.attrs:
            variant_name = link_tag['title']
            variant_url = link_tag['href']
            raw_price = price_tag.get_text(strip=True) if price_tag else "Price Not Available"

            # Clean the extracted price
            variant_price = clean_price(raw_price)

            # Store both URL and cleaned Price in dictionary
            variants[variant_name] = {
                "url": variant_url,
                "price": variant_price
            }

    return variants
