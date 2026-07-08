import os
import re
import pdfplumber

from datetime import datetime

from app.database.operations import (
    insert_record,
    fetch_all_records
)

from app.reports.excel import generate_excel


PDF_FOLDER = "data/pdfs"


def clean_text(value):

    if value is None:
        return ""

    value = value.replace("\n", " ")

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def normalize_date(date_value):

    if not date_value:
        return datetime.now().strftime("%d-%m-%Y")

    date_value = clean_text(date_value)

    formats = [
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%d-%m %Y",
        "%d.%m %Y"
    ]

    for fmt in formats:

        try:

            parsed = datetime.strptime(
                date_value,
                fmt
            )

            return parsed.strftime("%d-%m-%Y")

        except ValueError:
            continue

    return date_value


def detect_type(drug_name):

    name = drug_name.lower()

    if "bulk" in name:
        return "Bulk Drug"

    if "tablet" in name:
        return "Tablet"

    if "capsule" in name:
        return "Capsule"

    if "injection" in name:
        return "Injection"

    if "cream" in name:
        return "Cream"

    if "ointment" in name:
        return "Ointment"

    if "spray" in name:
        return "Spray"

    if "solution" in name:
        return "Solution"

    return "New Drug"


def create_record(
    drug_name,
    indication,
    approval_date,
    filename
):

    return {

        "category": "New Drug",

        "drug_name": clean_text(drug_name),

        "approval_date": normalize_date(
            approval_date
        ),

        "type": detect_type(drug_name),

        "composition": "Not Available",

        "dosage": "Not Available",

        "indication": (
            clean_text(indication)
            if clean_text(indication)
            else "Not Available"
        ),

        "manufacturer": "Not Available",

        "needs_enrichment": "Yes",

        "missing_fields": (
            "composition, dosage"
            if clean_text(indication)
            else "composition, dosage, indication"
        ),

        "source": "CDSCO PDF",

        "source_url": filename,

        "last_updated": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }


def extract_pdf(pdf_path):

    records = []

    current_record = None

    filename = os.path.basename(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                for row in table:

                    if not row or len(row) < 4:
                        continue

                    serial = clean_text(row[0])
                    drug_name = clean_text(row[1])
                    indication = clean_text(row[2])
                    date = clean_text(row[3])

                    # Skip table header
                    if (
                        "s.no" in serial.lower()
                        or "name of drug" in drug_name.lower()
                        or "name of new drug" in drug_name.lower()
                    ):
                        continue

                    # New numbered record
                    if re.match(r"^\d+\.?$", serial):

                        if current_record:

                            records.append(
                                create_record(
                                    current_record["drug_name"],
                                    current_record["indication"],
                                    current_record["date"],
                                    filename
                                )
                            )

                        current_record = {
                            "drug_name": drug_name,
                            "indication": indication,
                            "date": date
                        }

                    # Continuation from previous page/row
                    elif current_record:

                        if drug_name:

                            current_record["drug_name"] += (
                                " " + drug_name
                            )

                        if indication:

                            current_record["indication"] += (
                                " " + indication
                            )

                        if date and not current_record["date"]:

                            current_record["date"] = date

        if current_record:

            records.append(
                create_record(
                    current_record["drug_name"],
                    current_record["indication"],
                    current_record["date"],
                    filename
                )
            )

    return records


def import_all_pdfs():

    total_found = 0
    total_inserted = 0

    for filename in os.listdir(PDF_FOLDER):

        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(
            PDF_FOLDER,
            filename
        )

        print(
            f"\nReading PDF: {filename}"
        )

        records = extract_pdf(pdf_path)

        print(
            f"Extracted {len(records)} records"
        )

        total_found += len(records)

        for record in records:

            if insert_record(record):

                total_inserted += 1

    print("\n============================")

    print(
        f"Total PDF records found: {total_found}"
    )

    print(
        f"New records inserted: {total_inserted}"
    )

    print("============================")

    all_records = fetch_all_records()

    generate_excel(
        all_records,
        "data/exports/cdsco_approvals.xlsx"
    )

    print(
        "Excel regenerated with all database records."
    )


if __name__ == "__main__":

    import_all_pdfs()