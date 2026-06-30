from app.enrichment.search import search_drug
from app.enrichment.llm import enrich_drug

record = {
    "drug_name": "L-Carnitine L-Tartrate",
    "manufacturer": "Symbio Generics",
    "composition": "Not Available",
    "dosage": "Not Available",
    "indication": "Not Available"
}

results = search_drug(
    record["drug_name"],
    record["manufacturer"]
)

context = ""

for i, r in enumerate(results, start=1):

    context += f"""
Result {i}

Title:
{r["title"]}

URL:
{r["url"]}

Content:
{r["content"]}

"""

answer = enrich_drug(record, context)

print(answer)