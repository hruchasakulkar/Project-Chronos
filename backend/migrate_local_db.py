import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "chronos.db"


def column_names(connection, table_name):
    return {
        row[1]
        for row in connection.execute(
            f"PRAGMA table_info({table_name})"
        ).fetchall()
    }


def main():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        connection.execute("PRAGMA foreign_keys = ON")

        teams_columns = column_names(connection, "teams")

        if "id" not in teams_columns and "team_id" in teams_columns:
            print("renaming teams.team_id -> teams.id...")
            connection.execute(
                "ALTER TABLE teams RENAME COLUMN team_id TO id"
            )
        elif "id" in teams_columns:
            print("teams.id already exists; skipping team id rename.")
        else:
            raise RuntimeError(
                "teams table has neither 'team_id' nor 'id'. "
                "Refusing to guess the schema."
            )

        teams_columns = column_names(connection, "teams")

        # The current Round 2 service uses the master-schema names.
        # Keep the older r2_* columns intact so existing local test data
        # is not destroyed.
        if "round2_score" not in teams_columns:
            print("adding teams.round2_score...")
            connection.execute(
                "ALTER TABLE teams ADD COLUMN round2_score FLOAT DEFAULT 0.0"
            )

        if "round2_started_at" not in teams_columns:
            print("adding teams.round2_started_at...")
            connection.execute(
                "ALTER TABLE teams ADD COLUMN round2_started_at DATETIME"
            )

        if "round2_completed_at" not in teams_columns:
            print("adding teams.round2_completed_at...")
            connection.execute(
                "ALTER TABLE teams ADD COLUMN round2_completed_at DATETIME"
            )

        # Preserve existing local Round 2 score/start data in the new
        # canonical columns. r2_end_time is the old timer-end field, not
        # the completion timestamp, so it is deliberately not copied to
        # round2_completed_at.
        connection.execute(
            """
            UPDATE teams
            SET
                round2_score = COALESCE(round2_score, r2_score, 0.0),
                round2_started_at = COALESCE(
                    round2_started_at,
                    r2_start_time
                )
            """
        )

        connection.commit()

        # Verify every FK that points to teams now targets teams.id.
        bad_fks = []
        for (table_name,) in connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ):
            for fk in connection.execute(
                f"PRAGMA foreign_key_list({table_name})"
            ).fetchall():
                # PRAGMA foreign_key_list columns:
                # (id, seq, table, from, to, on_update, on_delete, match)
                if fk[2] == "teams" and fk[4] != "id":
                    bad_fks.append(
                        f"{table_name}.{fk[3]} -> teams.{fk[4]}"
                    )

        if bad_fks:
            raise RuntimeError(
                "Migration completed, but these foreign keys still "
                "target a non-canonical teams column:\n"
                + "\n".join(f"  - {item}" for item in bad_fks)
            )

        fk_errors = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if fk_errors:
            raise RuntimeError(
                "foreign_key_check reported violations:\n"
                + "\n".join(str(tuple(row)) for row in fk_errors)
            )

        print()
        print("local database migration completed successfully.")
        print("canonical team key: teams.id")
        print()
        print("teams:")
        for row in connection.execute(
            "SELECT id, team_name FROM teams ORDER BY id"
        ):
            print(f"  {row['id']}: {row['team_name']}")

        print()
        print("round 2 columns:")
        print("  round2_score")
        print("  round2_started_at")
        print("  round2_completed_at")

        print()
        print("all team foreign keys now target teams.id.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
