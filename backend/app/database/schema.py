from .connection import get_connection


def create_tables():
    connection = get_connection()

    try:
        connection.executescript("""
            -- =========================
            -- MASTER TEAMS TABLE
            -- =========================

            CREATE TABLE IF NOT EXISTS teams (
                team_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL UNIQUE,
                member1_name TEXT NOT NULL,
                member2_name TEXT NOT NULL,
                member1_prn TEXT NOT NULL,
                member2_prn TEXT NOT NULL,

                -- Round 1
                r1_start_time DATETIME,
                r1_end_time DATETIME,
                r1_time_diff FLOAT,
                r1_score FLOAT DEFAULT 0.0,
                r1_scaled FLOAT DEFAULT 0.0,

                -- Round 2 & Round 3
                r2_score FLOAT DEFAULT 0.0,
                r3_score FLOAT DEFAULT 0.0,
                total_score FLOAT DEFAULT 0.0,

                -- Game progression
                status TEXT DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE', 'FINISHED', 'DISQUALIFIED')),
                current_state TEXT DEFAULT 'REGISTERED',

                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );


            -- =========================
            -- ROUND 1
            -- =========================

            CREATE TABLE IF NOT EXISTS round1_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                correct_era TEXT NOT NULL
                    CHECK(correct_era IN ('PAST', 'PRESENT', 'FUTURE')),
                clue_text TEXT,
                points_positive FLOAT DEFAULT 2.0,
                points_negative FLOAT DEFAULT 1.0,
                is_active INTEGER DEFAULT 1
            );


            CREATE TABLE IF NOT EXISTS round1_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                selected_era TEXT NOT NULL
                    CHECK(selected_era IN ('PAST', 'PRESENT', 'FUTURE')),
                is_correct INTEGER NOT NULL,
                points_awarded FLOAT NOT NULL,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (item_id)
                    REFERENCES round1_items(item_id)
            );


            -- =========================
            -- ROUND 2
            -- =========================

            CREATE TABLE IF NOT EXISTS round2_files (
                file_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                timeline_tag TEXT NOT NULL,
                filename TEXT NOT NULL,
                content_text TEXT NOT NULL,
                is_locked INTEGER DEFAULT 0
            );


            CREATE TABLE IF NOT EXISTS round2_chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                question_number INTEGER NOT NULL,
                user_prompt TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                points_deducted FLOAT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS round2_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                suspect_identified TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                points_awarded FLOAT NOT NULL,
                ai_points_remaining FLOAT NOT NULL,
                round2_total_score FLOAT NOT NULL,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE CASCADE
            );


            -- =========================
            -- ROUND 3
            -- =========================

            CREATE TABLE IF NOT EXISTS round3_team_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER UNIQUE NOT NULL,
                case_id TEXT NOT NULL,
                culprit_candidate_id TEXT NOT NULL,
                valid_evidence_ids TEXT NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS round3_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                selected_candidate_id TEXT NOT NULL,
                selected_evidence_ids TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                points_awarded FLOAT NOT NULL,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE CASCADE
            );


            -- =========================
            -- GAME LOGS
            -- =========================

            CREATE TABLE IF NOT EXISTS game_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (team_id)
                    REFERENCES teams(team_id)
                    ON DELETE SET NULL
            );
        """)

        connection.commit()

    finally:
        connection.close()