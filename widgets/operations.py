from .models import ShoppingListItem
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    "User-Agent": "Mozilla/5.0"
}
def push_item(user,item_name,item_link,item_price):
    if item_price is None or item_price.lower()=="auto":
        try:
            item_price = extract_price(item_link)
        except:
            print("error getting price automatically.")
            item_price = 0
    if item_price is None:
        print("couldnt fetch price")
        item_price = 0
    new_item = ShoppingListItem(user=user,name=item_name,price=item_price,link=item_link)
    new_item.save()

def fetch_html(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except:
        return None

def extract_jsonld_price(soup):
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                offers = data.get("offers")
                if isinstance(offers, dict):
                    return offers.get("price")
        except:
            continue
    return None

def extract_meta_price(soup):
    for meta in soup.find_all("meta"):
        if meta.get("property", "").lower() in ["product:price:amount", "og:price:amount"]:
            return meta.get("content")
        if meta.get("name", "").lower() in ["price", "twitter:data1"]:
            return meta.get("content")
    return None

def extract_text_price(soup):
    text = soup.get_text(separator=' ', strip=True)
    prices = re.findall(r'[\$₹€]\s?[0-9,.]+', text)
    if prices:
        return prices[0]  # return first reasonable match
    return None

def extract_price(url):
    html = fetch_html(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "html.parser")

    # Strategy 1: JSON-LD
    price = extract_jsonld_price(soup)
    if price:
        return price

    # Strategy 2: Meta Tags
    price = extract_meta_price(soup)
    if price:
        return price

    # Strategy 3: Regex scan
    price = extract_text_price(soup)
    return price

def list_exists(user)->bool:
    shopping_list = ShoppingListItem.objects.filter(user=user)
    if shopping_list.exists():
        print("user has somethings stored")
        return True
    else:
        return False

# Fetch all shopping list items for a user
def get_shopping_list(user):
    return ShoppingListItem.objects.filter(user=user)



    
