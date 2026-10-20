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

            last_updated TEXT,
            is_new BOOLEAN DEFAULT FALSE,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        ALTER TABLE approvals ADD COLUMN IF NOT EXISTS is_new BOOLEAN DEFAULT FALSE;
        ALTER TABLE approvals ADD COLUMN IF NOT EXISTS added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

        CREATE TABLE IF NOT EXISTS approval_icd_mappings (

            id SERIAL PRIMARY KEY,

            approval_hash TEXT REFERENCES approvals(approval_hash) ON DELETE CASCADE,

            icd_search_term TEXT,
            icd_code TEXT,
            icd_indication TEXT,
            level_1_indication TEXT,

            UNIQUE (approval_hash, icd_search_term, icd_code)
        );

        -- Synchronize sequences if data was restored or imported with manual IDs
        SELECT setval(
            pg_get_serial_sequence('approvals', 'id'),
            COALESCE((SELECT MAX(id) FROM approvals), 0) + 1,
            false
        );
        SELECT setval(
            pg_get_serial_sequence('approval_icd_mappings', 'id'),
            COALESCE((SELECT MAX(id) FROM approval_icd_mappings), 0) + 1,
            false
        );
        """
    )

    conn.commit()

    cur.close()

    conn.close()