import hashlib

from app.database.db import get_connection


def generate_hash(record):
    """
    Generates a unique hash for each approval.
    """

    unique_string = (
        f"{record['drug_name']}|"
        f"{record['manufacturer']}|"
        f"{record['approval_date']}"
    )

    return hashlib.sha256(unique_string.encode()).hexdigest()


def approval_exists(approval_hash):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 1
        FROM approvals
        WHERE approval_hash = %s;
        """,
        (approval_hash,)
    )

    exists = cur.fetchone() is not None

    cur.close()
    conn.close()

    return exists


def insert_record(record):
    
    approval_hash = generate_hash(record)

    if approval_exists(approval_hash):
        return False

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO approvals (

            approval_hash,

            category,
            drug_name,
            approval_date,
            type,

            composition,
            dosage,
            indication,

            manufacturer,

            needs_enrichment,
            missing_fields,

            source,
            source_url,

            composition_source,
            dosage_source,
            indication_source,

            last_updated,
            is_new

        )

        VALUES (
            %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s,
            %s, %s,
            %s, %s,
            %s, %s, %s,
            %s,
            %s
        );
        """,

        (
            approval_hash,

            record["category"],
            record["drug_name"],
            record["approval_date"],
            record["type"],

            record["composition"],
            record["dosage"],
            record["indication"],

            record["manufacturer"],

            record["needs_enrichment"],
            record["missing_fields"],

            record["source"],
            record["source_url"],

            "",
            "",
            "",

            record["last_updated"],
            True
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    return True

def fetch_pending_enrichment():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        category,
        drug_name,
        approval_date,
        type,
        composition,
        dosage,
        indication,
        manufacturer,
        needs_enrichment,
        missing_fields,
        source,
        source_url,
        last_updated,
        composition_source,
        dosage_source,
        indication_source,
        is_new,
        added_at
        FROM approvals
        WHERE needs_enrichment='Yes';
        """
    )

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def fetch_all_records():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
        category,
        drug_name,
        approval_date,
        type,
        composition,
        dosage,
        indication,
        manufacturer,
        needs_enrichment,
        missing_fields,
        source,
        source_url,
        last_updated,
        composition_source,
        dosage_source,
        indication_source,
        is_new,
        added_at
        FROM approvals
        ORDER BY approval_date DESC;
        """
    )

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]
def update_enrichment(record):
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE approvals
        SET
            composition=%s,
            dosage=%s,
            indication=%s,

            composition_source=%s,
            dosage_source=%s,
            indication_source=%s,

            needs_enrichment=%s,
            missing_fields=%s,
            last_updated=%s

        WHERE approval_hash=%s;
        """,

        (
            record["composition"],
            record["dosage"],
            record["indication"],

            record["composition_source"],
            record["dosage_source"],
            record["indication_source"],

            record["needs_enrichment"],
            record["missing_fields"],
            record["last_updated"],

            generate_hash(record)
        )

    )

    conn.commit()
    

    cur.close()
    conn.close()
from datetime import datetime


def update_enrichment(record):

    approval_hash = generate_hash(record)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE approvals
        SET
            composition=%s,
            dosage=%s,
            indication=%s,

            composition_source=%s,
            dosage_source=%s,
            indication_source=%s,

            needs_enrichment=%s,
            missing_fields=%s,

            last_updated=%s

        WHERE approval_hash=%s;
        """,

        (
            record["composition"],
            record["dosage"],
            record["indication"],

            record["composition_source"],
            record["dosage_source"],
            record["indication_source"],

            record["needs_enrichment"],
            record["missing_fields"],

            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            approval_hash
        )
    )

    conn.commit()

    cur.close()
    conn.close()
    
def clear_new_flags():
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE approvals
        SET is_new = FALSE
        WHERE is_new = TRUE;
    """)

    conn.commit()

    cur.close()
    conn.close()
    
def fetch_pending_icd():
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            category,
            drug_name,
            approval_date,
            indication,
            manufacturer
        FROM approvals
        WHERE indication IS NOT NULL
            AND indication != ''
            AND indication != 'Not Available'

            AND NOT EXISTS (

                SELECT 1

                FROM approval_icd_mappings m

                 WHERE m.approval_hash =
                approvals.approval_hash
  );
        """
    )

    rows = cur.fetchall()

    columns = [
        desc[0]
        for desc in cur.description
    ]

    cur.close()
    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def update_icd_mapping(
    record,
    icd_result
):

    approval_hash = generate_hash(record)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE approvals
        SET
            icd_search_term = %s,
            icd_code = %s,
            icd_indication = %s,
            level_1_indication = %s
        WHERE approval_hash = %s;
        """,

        (
            icd_result["icd_search_term"],
            icd_result["icd_code"],
            icd_result["icd_indication"],
            icd_result["level_1_indication"],
            approval_hash
        )
    )

    conn.commit()

    cur.close()
    conn.close()
    
def insert_icd_mapping(
    record,
    icd_result
):

    approval_hash = generate_hash(record)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO approval_icd_mappings (

            approval_hash,
            icd_search_term,
            icd_code,
            icd_indication,
            level_1_indication

        )

        VALUES (%s, %s, %s, %s, %s)

        ON CONFLICT (
            approval_hash,
            icd_search_term,
            icd_code
        )

        DO UPDATE SET

            icd_indication =
                EXCLUDED.icd_indication,

            level_1_indication =
                EXCLUDED.level_1_indication;
        """,

        (
            approval_hash,

            icd_result["icd_search_term"],
            icd_result["icd_code"],
            icd_result["icd_indication"],
            icd_result["level_1_indication"]
        )
    )

    conn.commit()

    cur.close()
    conn.close()


def fetch_icd_mappings():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            approval_hash,
            icd_search_term,
            icd_code,
            icd_indication,
            level_1_indication,
            created_at

        FROM approval_icd_mappings

        ORDER BY created_at DESC;
        """
    )

    rows = cur.fetchall()

    columns = [
        desc[0]
        for desc in cur.description
    ]

    cur.close()
    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def delete_icd_mappings_for_record(record):

    approval_hash = generate_hash(record)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM approval_icd_mappings
        WHERE approval_hash = %s;
        """,
        (approval_hash,)
    )

    conn.commit()

    cur.close()
    conn.close()
    
def fetch_icd_mappings_for_excel():
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            a.drug_name,
            a.manufacturer,
            a.approval_date,
            a.indication AS original_indication,

            m.icd_search_term AS specific_indication,
            m.icd_code,
            m.icd_indication,
            m.level_1_indication

        FROM approval_icd_mappings m

        JOIN approvals a
            ON a.approval_hash = m.approval_hash

        ORDER BY
            a.approval_date DESC,
            a.drug_name,
            m.icd_search_term;
        """
    )

    rows = cur.fetchall()

    columns = [
        desc[0]
        for desc in cur.description
    ]

    cur.close()
    conn.close()

    return [
        dict(zip(columns, row))
        for row in rows
    ]