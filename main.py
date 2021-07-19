import requests
from bs4 import BeautifulSoup
import lxml
from branches import branches
from logo import logo
 
ADD_TO_BASKET_ENDPOINT = "https://www.expert.de/_api/shoppingcart/addItem"
 
print(logo)
loop = True
 
# Verify valid product URL and reduce it to its bare minimum
while loop == True:
    url = input("Bitte Produkt-URL von expert eingeben: ")
    if not "www.expert.de" in url or not ".html" in url:
        print("Da stimmt irgendwas nicht. Handelt es sich wirklich um eine gültige URL von expert?")
    else:
        url = url.split(".html")[0] + ".html"
        loop = False
 
# Define variables needed for further use
branches_amount = len(branches)
counter = 0
best_price = 999999
second_best_price = 999999
best_price_branches = []
second_best_price_branches = []
branch_ids = []
 
# Put branch ids into a list to allow for optional slicing
for branch in branches:
    branch_ids.append(branch)
 
with requests.Session() as session:
    # Get initial data necessary for API requests
    print("Initialisierung...")
    response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = response.text
    soup = BeautifulSoup(data, "lxml")
    csrf_token = soup.find("meta", {"name": "csrf-token"})["content"]
    element = soup.find("div", class_="widget-ArticleStatus")
    article_id = element["data-article-id"]
    article_number = element["data-article-number"]
    cart_id = element["data-cart-id"]
 
    # Generate parameters and headers
    params = {
        "shoppingCartId": cart_id,
        "quantity": 1,
        "article": article_id
    }
 
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json; charset=utf-8",
        "csrf-token": csrf_token,
    }
 
    # Iterate through branch_ids and create mydealz-compatible URL
    for branch_id in branch_ids:
        counter += 1
        print(f"\rFilialen überprüfen: {counter}/{branches_amount}", end="")
        session.cookies.set("fmarktcookie", f"e_{branch_id}", domain="www.expert.de", path="/")
        final_url = f"{url}?branch_id={branch_id}&gclid=0"
        # Request product price for each branch
        try:
            response = session.post(ADD_TO_BASKET_ENDPOINT, json=params, headers=headers)
            data = response.json()
            basket_branch = data["shoppingCart"]["itemList"]["items"][0]["price"]["customData"]["expPrice"]["onlineStore"]
            price = data["shoppingCart"]["itemList"]["items"][0]["price"]["gross"]
            branch = branches[branch_id]
            # Compare branch price with previous best price/second best price: discard if higher and save if lower or equal
            if price < best_price:
                second_best_price = best_price
                second_best_price_branches = best_price_branches
                best_price = price
                best_price_branches = [f"{branch}: {final_url}"]
            elif price == best_price:
                best_price_branches.append(f"{branch}: {final_url}")
            else:
                if price < second_best_price:
                    second_best_price = price
                    second_best_price_branches = [f"{branch}: {final_url}"]
                elif price == second_best_price:
                    second_best_price_branches.append(f"{branch}: {final_url}")
        except KeyError:
            pass
 
 
# Print branches for best price and second best price if there is an actual entry
if best_price != 999999:
    print(f"\n\nDer Bestpreis liegt bei {best_price}€. Folgende Filialen bieten diesen Preis an: ")
    for branch in best_price_branches:
        print(branch)
    if second_best_price != 999999:
        print(f"\nDer zweitbeste Preis liegt bei {second_best_price}€. Folgende Filialen bieten diesen Preis an: ")
        for branch in second_best_price_branches:
            print(branch)
else:
    print("\nKeine Angebote gefunden.")
 
input('\nDrücke "Enter" zum Beenden.')
