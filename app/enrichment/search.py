import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def tavily_search(drug_name, manufacturer):
    
    query = f"{drug_name} {manufacturer} composition dosage indication"

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=3
    )

    formatted = ""

    for i, result in enumerate(response["results"], start=1):

        formatted += f"""
Result {i}

Title:
{result.get("title","")}

URL:
{result.get("url","")}

Content:
{result.get("content","")}

---------------------------------------

"""

    return formatted