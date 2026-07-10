import os
import re

from dotenv import load_dotenv
from tavily import TavilyClient

from app.icd.search import get_icd_entity


load_dotenv()


tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def extract_codes(text):

    if not text:
        return []

    codes = re.findall(
        r"\b[A-Z][0-9]{2}(?:\.[0-9])?\b",
        text.upper()
    )

    return list(dict.fromkeys(codes))


def search_icd_codes(search_term):

    query = (
        f'WHO ICD-10 2019 "{search_term}" '
        f'ICD code'
    )

    print(
        f"\nSearching ICD for: {search_term}"
    )

    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=5
    )

    possible_codes = []


    for result in response.get(
        "results",
        []
    ):

        text = (
            result.get("title", "")
            + " "
            + result.get("content", "")
        )

        codes = extract_codes(text)

        possible_codes.extend(codes)


    possible_codes = list(
        dict.fromkeys(possible_codes)
    )

    print(
        "Possible codes:",
        possible_codes
    )

    return possible_codes


def validate_codes(codes):

    validated = []


    for code in codes:

        try:

            data = get_icd_entity(code)

            title = (
                data.get("title", {})
                .get("@value", "")
            )

            validated.append(
                {
                    "code": code,
                    "title": title
                }
            )

            print(
                f"WHO VALID: {code} → {title}"
            )


        except Exception:

            pass


    return validated

def split_indication_into_terms(indication):
    
    text = indication.strip()

    # Remove common introductory drug/therapy language
    text = re.sub(
        r"(?i)^.*?\bis indicated for the treatment of\b",
        "",
        text
    )

    text = re.sub(
        r"(?i)^.*?\bis indicated for\b",
        "",
        text
    )

    text = re.sub(
        r"(?i)^for the treatment of\b",
        "",
        text
    )

    text = re.sub(
        r"(?i)^the treatment of\b",
        "",
        text
    )

    # Remove patient population wording
    text = re.sub(
        r"(?i)^adult and pediatric patients "
        r"\d+ years and older with\s*",
        "",
        text
    )

    text = re.sub(
        r"(?i)^patients with\s*",
        "",
        text
    )

    # Remove treatment-history qualifiers
    text = re.sub(
        r"(?i)\s+after failure of.*$",
        "",
        text
    )

    text = re.sub(
        r"(?i)\s+who have received.*$",
        "",
        text
    )

    text = re.sub(
        r"(?i)\s+following.*$",
        "",
        text
    )

    # Split multiple indication sections
    parts = re.split(
        r",\s*(?=the treatment of|treatment of|for the treatment of)",
        text,
        flags=re.IGNORECASE
    )

    terms = []

    for part in parts:

        part = re.sub(
            r"(?i)^the treatment of\s*",
            "",
            part
        )

        part = re.sub(
            r"(?i)^treatment of\s*",
            "",
            part
        )

        part = re.sub(
            r"(?i)^for the treatment of\s*",
            "",
            part
        )

        part = part.strip(" .,")

        if part:
            terms.append(part)

    return terms

def get_best_match(search_term):
    
    codes = search_icd_codes(search_term)

    validated = validate_codes(codes)

    if not validated:
        return None

    term = search_term.lower()

    # ---------------------------------
    # Disease-specific preference rules
    # ---------------------------------

    preferred_codes = []

    # Age-related macular degeneration
    if (
        "macular degeneration" in term
        or "age related macular" in term
    ):
        preferred_codes = [
            "H35.3"
        ]

    # Diabetic macular oedema / retinopathy
    elif (
        "diabetic macular" in term
        or "diabetic retinopathy" in term
    ):
        preferred_codes = [
            "H36.0",
            "H36"
        ]

    # Retinal vein occlusion
    elif (
        "retinal vein occlusion" in term
        or "rvo" in term
    ):
        preferred_codes = [
            "H34"
        ]

    # Choroidal neovascularisation
    elif (
        "choroidal neovascular" in term
        or "choroidal neovascularisation" in term
        or "choroidal neovascularization" in term
    ):
        preferred_codes = [
            "H31.8",
            "H31",
            "H35"
        ]

    # Pertussis
    elif (
        "pertussis" in term
        or "whooping cough" in term
    ):
        preferred_codes = [
            "A37.9",
            "A37"
        ]

    # COPD
    elif (
        "chronic obstructive pulmonary disease" in term
        or "copd" in term
    ):

        if (
            "acute lower respiratory infection" in term
            or "respiratory infection" in term
        ):
            preferred_codes = [
                "J44.0"
            ]

        elif "acute exacerbation" in term:
            preferred_codes = [
                "J44.1"
            ]

        else:
            preferred_codes = [
                "J44.9",
                "J44"
            ]

    # ---------------------------------
    # Try preferred WHO-validated codes
    # ---------------------------------

    for preferred_code in preferred_codes:

        for candidate in validated:

            if candidate["code"] == preferred_code:
                return candidate

    # ---------------------------------
    # Fallback ranking
    # ---------------------------------

    term_words = set(
        re.findall(
            r"[a-z]+",
            term
        )
    )

    def relevance(candidate):

        title_words = set(
            re.findall(
                r"[a-z]+",
                candidate["title"].lower()
            )
        )

        overlap = len(
            term_words.intersection(
                title_words
            )
        )

        return overlap

    validated.sort(
        key=relevance,
        reverse=True
    )

    return validated[0]

    def relevance(candidate):

        title_words = set(
            re.findall(
                r"[a-z]+",
                candidate["title"].lower()
            )
        )

        overlap = len(
            term_words.intersection(
                title_words
            )
        )

        return overlap


    validated.sort(
        key=relevance,
        reverse=True
    )

    return validated[0]

if __name__ == "__main__":

    test_terms = [
        "Pertussis",
        "Age Related Macular Degeneration",
        "Diabetic Macular Oedema",
        "Retinal Vein Occlusion",
        "Choroidal Neovascularisation"
    ]


    for term in test_terms:

        print(
            "\n============================"
        )

        print(
            "TERM:",
            term
        )

        result = get_best_match(
            term
        )

        print(
            "BEST MATCH:",
            result
        )