from app.database.db import get_connection


def create_tables():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals (

            id SERIAL PRIMARY KEY,

            approval_hash TEXT UNIQUE,

            category TEXT,
            drug_name TEXT,
            approval_date TEXT,
            type TEXT,

            composition TEXT,
            dosage TEXT,
            indication TEXT,

            manufacturer TEXT,

            needs_enrichment TEXT,
            missing_fields TEXT,

            source TEXT,
            source_url TEXT,

            composition_source TEXT,
            dosage_source TEXT,
            indication_source TEXT,

            last_updated TEXT
        );
        """
    )

    conn.commit()

    cur.close()

    conn.close()