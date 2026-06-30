import os
import json
import logging
import json
import logging

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

logger = logging.getLogger(__name__)


def enrich_record(record, search_results):
    """
    Enrich a CDSCO drug record using Gemini.

    Parameters
    ----------
    record : dict
        Drug record from CDSCO.

    search_results : str
        Formatted Tavily search results.

    Returns
    -------
    dict
        {
            "composition": {
                "value": "...",
                "source": "..."
            },
            "dosage": {
                "value": "...",
                "source": "..."
            },
            "indication": {
                "value": "...",
                "source": "..."
            }
        }
    """

    prompt = f"""
You are an expert pharmaceutical data extraction assistant.

Your job is to enrich missing information in CDSCO drug approval records.

------------------------------------------------------------

Drug Name:
{record["drug_name"]}

Manufacturer:
{record["manufacturer"]}

Current CDSCO Record

Composition:
{record["composition"]}

Dosage:
{record["dosage"]}

Indication:
{record["indication"]}

------------------------------------------------------------

Search Results

{search_results}

------------------------------------------------------------

Instructions

1. Fill ONLY fields whose value is "Not Available".

2. Use ONLY information explicitly present in the search results.

3. Never infer information from the drug name.

4. Never use your own pharmaceutical or medical knowledge.

5. If information is missing, return "Not Available".

6. Every extracted field MUST have its own source URL.

7. Preserve wording from the source whenever possible.

8. Return ONLY valid JSON.

9. No markdown.

10. No code fences.

Return exactly:

{{
    "composition": {{
        "value": "...",
        "source": "https://..."
    }},
    "dosage": {{
        "value": "...",
        "source": "https://..."
    }},
    "indication": {{
        "value": "...",
        "source": "https://..."
    }}
}}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        result = json.loads(text)

        logger.info(
            f"Successfully enriched {record['drug_name']}"
        )

        return result

    except json.JSONDecodeError:

        logger.error(
            f"Gemini returned invalid JSON for {record['drug_name']}"
        )

        return {
            "composition": {
                "value": "Not Available",
                "source": ""
            },
            "dosage": {
                "value": "Not Available",
                "source": ""
            },
            "indication": {
                "value": "Not Available",
                "source": ""
            }
        }

    except Exception as e:

        logger.exception(
            f"Gemini failed for {record['drug_name']}: {e}"
        )

        return {
            "composition": {
                "value": "Not Available",
                "source": ""
            },
            "dosage": {
                "value": "Not Available",
                "source": ""
            },
            "indication": {
                "value": "Not Available",
                "source": ""
            }
        }