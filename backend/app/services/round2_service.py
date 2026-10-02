from ..database.connection import get_connection


def get_round2_files():
    """Return all Round 2 evidence files."""
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                file_id,
                project_name,
                timeline_tag,
                filename,
                content_text,
                is_locked
            FROM round2_files
            ORDER BY file_id
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_files_for_team(team_id: int):
    """
    Return Round 2 evidence files available to a team.

    Team-specific authentication/unlocking will be integrated
    once the final team authentication mechanism is connected.
    """
    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT
                file_id,
                project_name,
                timeline_tag,
                filename,
                content_text,
                is_locked
            FROM round2_files
            WHERE is_locked = 0
            ORDER BY file_id
        """).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def get_file_by_id(file_id: str, team_id: int):
    """
    Return one Round 2 evidence file if it is unlocked.
    """
    connection = get_connection()

    try:
        row = connection.execute("""
            SELECT
                file_id,
                project_name,
                timeline_tag,
                filename,
                content_text,
                is_locked
            FROM round2_files
            WHERE file_id = ?
              AND is_locked = 0
        """, (file_id,)).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()