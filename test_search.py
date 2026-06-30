from app.enrichment.search import search_drug

results = search_drug(
    "L-Carnitine L-Tartrate",
    "Symbio Generics"
)

for i, result in enumerate(results, start=1):

    print("=" * 80)

    print(f"Result {i}")

    print(result["title"])

    print(result["url"])

    print(result["content"])