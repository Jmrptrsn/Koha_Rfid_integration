import requests
import base64

# =============================
# Koha configuration
# =============================
KOHA_API_BASE = "http://192.168.0.149:8080/api/v1"
USERNAME = ""
PASSWORD = ""
TIMEOUT = 10

# =============================
# Auth headers
# =============================
def get_auth_headers():
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

# =============================
# Checkout by barcode
# =============================
def checkout_by_barcode():
    barcode = input("Enter book barcode: ").strip()

    # 1️⃣ Find the item
    try:
        res = requests.get(
            f"{KOHA_API_BASE}/items",
            headers=get_auth_headers(),
            timeout=TIMEOUT
        )
        res.raise_for_status()
        items = res.json()
    except Exception as e:
        print("❌ Failed to fetch items:", e)
        return

    matched_item = None
    for item in items:
        if item.get("external_id") == barcode:
            matched_item = item
            break

    if not matched_item:
        print("❌ No item found with that barcode.")
        return

    item_id = matched_item.get("item_id")
    biblio_id = matched_item.get("biblio_id")

    # 2️⃣ Fetch title
    title = "Unknown title"
    if biblio_id:
        try:
            biblio_res = requests.get(
                f"{KOHA_API_BASE}/biblios/{biblio_id}",
                headers=get_auth_headers(),
                timeout=TIMEOUT
            )
            if biblio_res.status_code == 200:
                title = biblio_res.json().get("title", title)
        except requests.exceptions.RequestException:
            pass

    print(f"\n📘 Book found: {title}")
    confirm = input("Do you want to check out this book? (y/n): ").strip().lower()
    if confirm != "y":
        print("❌ Checkout cancelled.")
        return

    patron_id = input("Enter patron ID: ").strip()

    payload = {
        "patron_id": int(patron_id),
        "item_id": int(item_id) 
    }

    # 3️⃣ Checkout the book
    try:
        checkout_res = requests.post(
            f"{KOHA_API_BASE}/checkouts",
            headers=get_auth_headers(),
            json=payload,
            timeout=TIMEOUT
        )
        checkout_res.raise_for_status()
        print("✅ Book successfully checked out!")
    except requests.exceptions.HTTPError:
        print("❌ Checkout failed:")
        print(checkout_res.text)
    except requests.exceptions.RequestException as e:
        print("❌ Connection error:", e)
