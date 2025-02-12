import pandas as pd
from variant_links import variant_links
from variant_data import variant_data


brand = 'hyundai'
model = 'i20'
url = f"https://www.cardekho.com/{brand}/{model}/specs"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

variant_list = variant_links(url, headers)

for variant_name, url in variant_list.items():
    all_variants_data = variant_data(variant_name, url, headers)

df = pd.DataFrame(all_variants_data)
df.to_csv(f"{brand}-{model}.csv", index=False)
print(f"{brand}-{model}.csv created successfully.")
