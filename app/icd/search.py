import os
import requests

from dotenv import load_dotenv


load_dotenv()


CLIENT_ID = os.getenv("WHO_ICD_CLIENT_ID")
CLIENT_SECRET = os.getenv("WHO_ICD_CLIENT_SECRET")


TOKEN_URL = (
    "https://icdaccessmanagement.who.int/connect/token"
)


def get_access_token():

    response = requests.post(
        TOKEN_URL,

        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "icdapi_access",
            "grant_type": "client_credentials"
        }
    )

    response.raise_for_status()

    return response.json()["access_token"]

    
def test_icd10_code(code):
    
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "API-Version": "v2",
        "Accept-Language": "en"
    }

    url = f"https://id.who.int/icd/release/10/2019/{code}"

    response = requests.get(
        url,
        headers=headers
    )

    print("STATUS:", response.status_code)
    print("\nRESPONSE:\n")
    print(response.text)

def get_icd_entity(code):
    
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "API-Version": "v2",
        "Accept-Language": "en"
    }

    url = f"https://id.who.int/icd/release/10/2019/{code}"

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    return response.json()

def test_parent_hierarchy(code):
    
    current_code = code

    print(f"\nHierarchy for {code}:\n")

    while current_code:

        data = get_icd_entity(current_code)

        title = (
            data.get("title", {})
            .get("@value", "Unknown")
        )

        print(f"{current_code} → {title}")

        parents = data.get("parent", [])

        if not parents:
            break

        parent_url = parents[0]

        # Stop when WHO hierarchy reaches ICD-10 release root
        release_root = (
            "http://id.who.int/icd/release/10/2019"
        )

        if parent_url.rstrip("/") == release_root:
            break

        current_code = parent_url.rstrip("/").split("/")[-1]    
        
def get_icd_hierarchy(code):
    
    hierarchy = []

    current_code = code

    release_root = (
        "http://id.who.int/icd/release/10/2019"
    )

    while current_code:

        data = get_icd_entity(current_code)

        title = (
            data.get("title", {})
            .get("@value", "Unknown")
        )

        hierarchy.append({
            "code": current_code,
            "title": title
        })

        parents = data.get("parent", [])

        if not parents:
            break

        parent_url = parents[0].rstrip("/")

        if parent_url == release_root:
            break

        current_code = parent_url.split("/")[-1]

    return hierarchy
    
if __name__ == "__main__":
    
    test_parent_hierarchy("A37.9")
       
