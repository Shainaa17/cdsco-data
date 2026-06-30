import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def tavily_search(drug_name, manufacturer):

    query = f"{drug_name} {manufacturer} composition indication"

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=3
    )

    return response["results"]