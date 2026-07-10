from app.icd.code_matcher import (
    split_indication_into_terms,
    get_best_match
)

from app.icd.search import get_icd_hierarchy

from app.database.operations import (
    fetch_pending_icd,
    insert_icd_mapping,
    fetch_all_records,
    fetch_icd_mappings_for_excel
)

from app.reports.excel import generate_excel_with_icd


OUTPUT_FILE = "data/exports/cdsco_approvals.xlsx"


def is_safe_mapping(term, result):

    if not result:
        return False

    term_lower = term.lower()
    code = result["code"]

    # Do not accept broad diabetes codes for
    # diabetic macular oedema
    if (
        "diabetic macular" in term_lower
        and not code.startswith(("H35", "H36"))
    ):
        print(
            f"SKIPPED unsafe mapping: "
            f"{term} → {code}"
        )

        return False

    return True


def map_term(term):

    print("\n------------------------------")
    print(f"Mapping: {term}")
    print("------------------------------")

    best = get_best_match(term)

    if not is_safe_mapping(term, best):
        return None

    hierarchy = get_icd_hierarchy(
        best["code"]
    )

    level_1 = ""

    if hierarchy:
        level_1 = hierarchy[-1]["title"]

    result = {
        "icd_search_term": term,
        "icd_code": best["code"],
        "icd_indication": best["title"],
        "level_1_indication": level_1
    }

    print("\nFINAL MAPPING:")

    print(
        f"{result['icd_search_term']} "
        f"→ {result['icd_code']} "
        f"→ {result['icd_indication']} "
        f"→ {result['level_1_indication']}"
    )

    return result


def run_icd_pipeline(limit=1):

    print("\n==============================")
    print("ICD DATABASE MAPPING PIPELINE")
    print("==============================\n")

    records = fetch_pending_icd()

    if limit is not None:
        records = records[:limit]

    print(
        f"{len(records)} records will be processed."
    )

    for index, record in enumerate(
        records,
        start=1
    ):

        print("\n================================")
        print(
            f"[{index}/{len(records)}] "
            f"{record['drug_name']}"
        )
        print("================================")

        indication = record["indication"]

        terms = split_indication_into_terms(
            indication
        )

        print("\nExtracted indication parts:")

        for term in terms:
            print(f"- {term}")

        saved_count = 0

        for term in terms:

            result = map_term(term)

            if not result:
                continue

            insert_icd_mapping(
                record,
                result
            )

            saved_count += 1

            print("Saved mapping to PostgreSQL.")

        print(
            f"\nSaved {saved_count} mappings "
            f"for {record['drug_name']}."
        )

    print("\nRegenerating Excel...")

    all_records = fetch_all_records()

    icd_records = fetch_icd_mappings_for_excel()

    generate_excel_with_icd(
        all_records,
        icd_records,
        OUTPUT_FILE
    )

    print("\nICD pipeline completed.")


if __name__ == "__main__":

    run_icd_pipeline(limit=10)