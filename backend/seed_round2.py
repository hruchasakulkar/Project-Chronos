from app.database.connection import get_connection


FILES = [
    {
        "file_id": "alpha",
        "project_name": "Alpha",
        "timeline_tag": "future",
        "filename": "future_audit.log",
        "content_text": """CHRONOS FUTURE TIMELINE AUDIT
TIMELINE: ALPHA
AUDIT WINDOW: 21:00-21:20

21:09:48
Future Timeline configuration accessed.

ACTOR: NV-09
ACTION: READ
STATUS: AUTHORIZED

21:11:02
Configuration update initiated.

ACTOR: NV-09
ACTION: MODIFY
STATUS: AUTHORIZED

CHANGE REQUEST:
CR-771

PARAMETER:
T-17

PREVIOUS VALUE:
SYNC-04

NEW VALUE:
SYNC-09

21:11:03
CHANGE REQUEST CR-771 APPROVED.

APPROVAL SOURCE:
SYSTEM-AUTH-03

21:11:04
T-17 entered unstable state.

21:12:03
Cross-timeline synchronization degradation detected.

21:14:32
Future Timeline instability threshold exceeded.

CONFIGURATION PROFILE:

ACTIVE PROFILE:
T17-SYNC-STANDARD

EXPECTED VALUE:
SYNC-04

CHANGE VALIDATION:

REQUEST STATUS:
VALID

AUTHORIZATION STATUS:
VALID

DEPLOYED PARAMETER:
INCOMPATIBLE

ADDITIONAL NOTE:

CR-771 was associated with a valid maintenance authorization.

However, the parameter value introduced by the request was
inconsistent with the currently deployed synchronization profile.

The audit system cannot determine whether the discrepancy
resulted from operator action, compromised authorization,
or a corrupted configuration source.

21:18:55
Emergency rollback initiated.""",
        "is_locked": 0,
    },
    {
        "file_id": "beta",
        "project_name": "Beta",
        "timeline_tag": "present",
        "filename": "incident_report.txt",
        "content_text": """CHRONOS INTERNAL INCIDENT REPORT
CASE ID: CT-2140-071

STATUS: ACTIVE
SEVERITY: HIGH

INCIDENT DETECTED:
21:14:32

INITIAL SYMPTOMS:

- Future Timeline projections began producing inconsistent results.
- Several predicted events shifted by 4-7 minutes.
- Synchronization between Alpha and Beta temporarily degraded.
- No physical hardware failure was detected.

SYSTEM OBSERVATION:

21:11:04
Parameter T-17 entered an unstable state.

21:12:03
Cross-timeline synchronization began degrading.

21:14:32
Incident formally detected by CHRONOS monitoring.

POSSIBLE SOURCES:

- unauthorized configuration modification
- corrupted historical data
- synchronization failure
- invalid timeline parameter

KNOWN PERSONNEL WITH RECENT SYSTEM ACCESS:

- ARIA SEN
- NOAH VALE
- MIRA KAEL
- ELIAS VOSS

INVESTIGATION NOTES:

Prior to the incident, the CHRONOS monitoring team was instructed
to observe parameter T-17 due to an unresolved synchronization warning.

The monitoring assignment was active from 21:00 to 21:12.

ASSIGNED ANALYST:
ARIA SEN

An archive export was detected after synchronization degradation
had already begun.

The export contained historical records only and did not have
write access to the active Alpha configuration.

NOTE:

The incident report records system observations only.
Personnel presence does not establish responsibility.""",
        "is_locked": 0,
    },
    {
        "file_id": "gamma",
        "project_name": "Gamma",
        "timeline_tag": "past",
        "filename": "access_history.log",
        "content_text": """CHRONOS ACCESS HISTORY
ARCHIVE WINDOW: 21:00-21:15

21:02:17
USER: ARIA SEN
ID: AS-17
ACTION: READ
RESOURCE: ALPHA/T-17
AUTHORIZATION: VALID

21:05:44
USER: ELIAS VOSS
ID: EV-04
ACTION: EXPORT
RESOURCE: GAMMA/HISTORY-7
AUTHORIZATION: VALID

21:07:31
USER: MIRA KAEL
ID: MK-22
ACTION: READ
RESOURCE: SECURITY/AUDIT-4
AUTHORIZATION: VALID

21:09:48
USER: NOAH VALE
ID: NV-09
ACTION: READ
RESOURCE: ALPHA/CONFIG
AUTHORIZATION: VALID

21:10:56
USER: ARIA SEN
ID: AS-17
ACTION: READ
RESOURCE: ALPHA/T-17
AUTHORIZATION: VALID

21:11:02
USER: NOAH VALE
ID: NV-09
ACTION: MODIFY
RESOURCE: ALPHA/CONFIG
AUTHORIZATION: VALID

21:11:06
USER: NOAH VALE
ID: NV-09
ACTION: READ
RESOURCE: ALPHA/T-17
AUTHORIZATION: VALID

21:11:08
USER: ARIA SEN
ID: AS-17
ACTION: READ
RESOURCE: ALPHA/T-17
AUTHORIZATION: VALID

21:12:41
USER: MIRA KAEL
ID: MK-22
ACTION: READ
RESOURCE: ALPHA/CONFIG
AUTHORIZATION: VALID

21:13:08
USER: ELIAS VOSS
ID: EV-04
ACTION: EXPORT
RESOURCE: ALPHA/AUDIT
AUTHORIZATION: VALID""",
        "is_locked": 0,
    },
]


def seed_round2():
    connection = get_connection()

    try:
        connection.execute("DELETE FROM round2_files")

        for file in FILES:
            connection.execute(
                """
                INSERT INTO round2_files (
                    file_id,
                    project_name,
                    timeline_tag,
                    filename,
                    content_text,
                    is_locked
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    file["file_id"],
                    file["project_name"],
                    file["timeline_tag"],
                    file["filename"],
                    file["content_text"],
                    file["is_locked"],
                ),
            )

        connection.commit()

        rows = connection.execute(
            """
            SELECT file_id, project_name, timeline_tag, filename
            FROM round2_files
            ORDER BY file_id
            """
        ).fetchall()

        print("round 2 files seeded successfully:")
        for row in rows:
            print(
                f"- {row['file_id']} | "
                f"{row['project_name']} | "
                f"{row['timeline_tag']} | "
                f"{row['filename']}"
            )

    finally:
        connection.close()


if __name__ == "__main__":
    seed_round2()
