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
    
       
if __name__ == "__main__":
    
    print("Testing ICD-10 code A37.9...\n")

    test_icd10_code("A37.9")