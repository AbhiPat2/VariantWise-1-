import requests
from bs4 import BeautifulSoup


def variant_links(url, headers):

    # Send GET request with headers
    response = requests.get(url, headers=headers)

    # Parse response
    soup = BeautifulSoup(response.text, 'html.parser')

    variants = {}
    for variant in soup.find_all('div', class_='variantCard shadow16 outervariant'):
        link_tag = variant.find('a', class_='link hover')
        if link_tag and 'title' in link_tag.attrs and 'href' in link_tag.attrs:
            variants[link_tag['title']] = link_tag['href']

    return variants
