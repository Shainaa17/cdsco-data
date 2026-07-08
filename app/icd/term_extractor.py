import os
import json
import logging

from dotenv import load_dotenv
from google import genai


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


logger = logging.getLogger(__name__)


def extract_indication_terms(indication):

    if (
        not indication
        or indication == "Not Available"
        or indication.lower().startswith("not applicable")
    ):

        return []


    prompt = f"""
You are a medical terminology extraction assistant.

Your task is to extract the specific diseases, disorders, infections,
conditions, or clinical indications mentioned in the text.

TEXT:

{indication}

RULES:

1. Extract only diseases, disorders, infections, syndromes,
   or medical conditions explicitly mentioned in the text.

2. Do not return treatment words such as:
   treatment, prevention, prophylaxis, therapy, management,
   immunization, or symptomatic relief.

3. Preserve specific disease names.

4. If multiple distinct conditions are mentioned,
   return all of them separately.

5. Do not generate ICD codes.

6. Do not infer conditions that are not explicitly present.

7. Return only valid JSON.

Return exactly this format:

{{
    "terms": [
        "condition 1",
        "condition 2"
    ]
}}
"""


    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown fences if Gemini adds them
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        result = json.loads(text)

        terms = result.get(
            "terms",
            []
        )

        logger.info(
            f"ICD search terms extracted: {terms}"
        )

        return terms


    except Exception as e:

        logger.exception(
            f"Term extraction failed: {e}"
        )

        return []