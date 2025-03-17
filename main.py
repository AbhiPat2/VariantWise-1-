import pandas as pd
from variant_links import variant_links
from variant_data import variant_data

brand = 'maruti'
model = 'baleno'
url = f"https://www.cardekho.com/{brand}/{model}/specs"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive"
}

# Fetch all variant links and prices
variant_list = variant_links(url, headers)

# Initialize a list to store all variants data
all_variants_data = []

# Iterate through each variant and fetch specifications
for variant_name, details in variant_list.items():
    variant_info = variant_data(variant_name, details["url"], headers, details["price"])
    
    # Ensure data is appended correctly
    if variant_info:
        all_variants_data.extend(variant_info)

# Convert to DataFrame and save
df = pd.DataFrame(all_variants_data)
df = df.drop_duplicates()
df.to_csv(f"{brand}-{model}.csv", index=False)
print(f"{brand}-{model}.csv created successfully.")
