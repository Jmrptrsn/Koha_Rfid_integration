import requests
from requests.auth import HTTPBasicAuth

koha_items_url = "http://192.168.0.149:8080/api/v1/items"
koha_biblio_url = "http://192.168.0.149:8080/api/v1/biblios"
username = ""
password = ""

# Fetch items
response = requests.get(koha_items_url, auth=HTTPBasicAuth(username, password))
items = response.json()

for item in items:
    barcode = item.get("external_id")  # <-- this is your barcode
    biblio_id = item.get("biblio_id")

    # Fetch title using biblio_id
    title = "No Title"
    if biblio_id:
        biblio_resp = requests.get(f"{koha_biblio_url}/{biblio_id}", auth=HTTPBasicAuth(username, password))
        if biblio_resp.status_code == 200:
            biblio = biblio_resp.json()
            title = biblio.get("title", "No Title")

    print(f"Title: {title} | Barcode: {barcode}")
