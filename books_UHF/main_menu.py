import requests
import base64
import json

# ✅ NEW: import checkout logic
from checkout_logic import checkout_by_barcode

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
# Generic GET helper
# =============================
def koha_get(endpoint, params=None):
    url = f"{KOHA_API_BASE}{endpoint}"
    try:
        response = requests.get(
            url,
            headers=get_auth_headers(),
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        print("❌ Koha returned an error:", response.status_code)
        print(response.text)
    except requests.exceptions.RequestException as e:
        print("❌ Connection error:", e)
    return None

# =============================
# Search books by title
# =============================
def search_books_by_title(title):
    query = {"title": {"-like": f"%{title}%"}}
    return koha_get("/biblios", params={"q": json.dumps(query)})

# =============================
# Get all books
# =============================
def get_all_books():
    query = {"title": {"-like": "%"}}
    return koha_get("/biblios", params={"q": json.dumps(query)})

# =============================
# Fetch items
# =============================
def fetch_items(biblio_id):
    return koha_get(f"/biblios/{biblio_id}/items")

# =============================
# Determine item status
# =============================
def get_item_status(item):
    if item.get("itemlost"):
        return "Lost"
    if item.get("onloan"):
        return "Checked out"
    if item.get("notforloan"):
        return "Not for loan"
    if item.get("withdrawn"):
        return "Withdrawn"
    return "Available"

# =============================
# Main program
# =============================
from checkout_logic import checkout_by_barcode

# =============================
# Main menu
# =============================
if __name__ == "__main__":
    while True:
        print("\n📚 Koha Book Status Checker (Raspberry Pi)")
        print("1. Search book by title")
        print("2. Show all books")
        print("3. Check out book by barcode")
        print("4. Exit")

        choice = input("Choose an option (1-4): ").strip()

        if choice == "1":
            # TODO: your existing search_books_by_title logic here
            print("🔹 Option 1 selected (search books).")
            pass

        elif choice == "2":
            # TODO: your existing show all books logic here
            print("🔹 Option 2 selected (show all books).")
            pass

        elif choice == "3":
            # ✅ Call the checkout logic
            checkout_by_barcode()

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid choice. Try again.")
