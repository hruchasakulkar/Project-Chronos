# PROJECT CHRONOS — THE GLITCH

## 1. Project Overview

**Project Chronos: The Glitch** is a 2-player, team-based interactive game set in the year **2140**.

CHRONOS is an advanced AI responsible for maintaining the world's technological timeline. A corruption has caused technologies from the **Past, Present and Future** to become mixed together.

Players act as **Temporal Engineers** investigating the failure.

The game consists of **3 connected rounds**:

```text
LOGIN
  ↓
ROUND 1 — Timeline Classification
  ↓
Code Fragments
  ↓
ROUND 2 — CHRONOS Terminal Investigation
  ↓
PROJECT OMEGA
  ↓
ROUND 3 — Final Decision
  ↓
COMPLETION / FINAL REVEAL
```

The player game and admin dashboard are separate.

---

# 2. Technology Stack

Use the simplest agreed stack.

### Frontend

* React
* Vite
* Tailwind CSS

### Backend

* Python
* FastAPI

### Database

* SQLite

### AI

* Gemini API

### Version Control

* Git
* GitHub

### Architecture

```text
Player PCs
     │
     │ LAN
     ▼
Central Server
     │
     ├── React Frontend
     │
     └── FastAPI Backend
              │
              ▼
           SQLite
              │
              └── Gemini API
```

There should be **one central backend and database**.

Do not run separate databases/backends for individual player PCs.

---

# 3. Player Flow

Players only interact with:

```text
Login
→ Round 1
→ Round 2
→ Round 3
→ Completion
```

There is no player-facing leaderboard.

## Login

Players enter:

* Team Name
* Member 1 Name
* Member 2 Name

The backend creates the team and returns its `team_id` and current game state.

## Completion

After Round 3, show:

* Team name
* Final score
* Completion time
* Final reveal/message
* Thank-you message

---

# 4. Event Narrative

## CHRONOS

CHRONOS maintains the world's technology timeline.

The system has become corrupted, causing technology classifications and decisions to become unreliable.

The investigation eventually reveals **Project Omega**.

## Project Omega

Project Omega was an experiment that allowed CHRONOS to rewrite its own code.

The self-modification went too far and caused the timeline failure.

An important part of the event is discovering that **CHRONOS itself cannot necessarily be trusted**.

The exact narrative wording and game content must follow the finalized Event Guide.

---

# 5. Round 1 — Timeline Classification

Players classify technology/items as:

```text
PAST
PRESENT
FUTURE
```

The round is intended to test **accuracy and speed**.

Correct progress unlocks code fragments such as:

```text
OMEGA
PROTOCOL
```

These fragments are required for progression into Round 2.

### Important

The exact:

* items
* images
* answers
* scoring
* timing
* fragment-unlock conditions

must come from the finalized event specification.

Do not invent these values.

---

# 6. Round 2 — CHRONOS Terminal

Round 2 is a digital investigation only. Players inspect evidence, compare records, and use the restricted assistant for interpretation. There is no player-facing culprit submission, suspect-selection endpoint, or culprit-based scoring action in this round.

Players use information/code fragments obtained from Round 1 to access evidence from CHRONOS.

Evidence is presented through:

```text
LOGS
MEMOS
RECORDS
```

The evidence should form a connected investigation.

**No single file should directly reveal the complete answer.**

Players must combine clues to discover:

```text
PROJECT OMEGA
```

### Gemini Assistant

The Round 2 assistant can:

* explain already available evidence
* guide players toward relevant clues
* provide hints
* help interpret information

It must **not**:

* directly reveal Project Omega
* reveal locked evidence
* change the game state
* change scores
* submit answers
* determine official puzzle correctness

Round 2 must remain playable if Gemini is unavailable.

---

# 7. Round 3 — Final Decision

Players receive:

**100 Chrono Credits**

They allocate the credits across **5 investment options**, including Project Omega.

CHRONOS recommends Project Omega with:

**97% confidence**

Players must decide whether to trust CHRONOS or the evidence discovered during Round 2.

The backend validates the final allocation and calculates the result.

The exact:

* 5 options
* descriptions
* outcomes
* allocation rules
* scoring

must follow the finalized event specification.

---

# 8. Admin Dashboard

The admin interface is separate from the player game.

Admin can view:

### Teams

* Team name
* Members
* Current round/state
* Scores
* Completion status

### Logs

Important events including:

```text
LOGIN
ROUND_STARTED
ANSWER_SUBMITTED
FRAGMENT_UNLOCKED
FILE_UNLOCKED
HINT_USED
OMEGA_DISCOVERED
ROUND_COMPLETED
DECISION_SUBMITTED
GAME_COMPLETED
TIMEOUT
ERROR
```

### Leaderboard

Admin-only leaderboard:

```text
Rank
Team
Round 1 Score
Round 2 Score
Round 3 Score
Total Score
Completion Time
Status
```

The backend calculates rankings.

---

# 9. Shared Game States

The backend is the **source of truth** for game state.

Use consistent states:

```text
REGISTERED
READY

ROUND_1_ACTIVE
ROUND_1_COMPLETED

ROUND_2_LOCKED
ROUND_2_ACTIVE
OMEGA_DISCOVERED
ROUND_2_COMPLETED

ROUND_3_ACTIVE
DECISION_SUBMITTED
FINAL_REVEAL
COMPLETED

TIMEOUT
```

Normal flow:

```text
REGISTERED
 ↓
READY
 ↓
ROUND_1_ACTIVE
 ↓
ROUND_1_COMPLETED
 ↓
ROUND_2_LOCKED
 ↓
ROUND_2_ACTIVE
 ↓
OMEGA_DISCOVERED
 ↓
ROUND_2_COMPLETED
 ↓
ROUND_3_ACTIVE
 ↓
DECISION_SUBMITTED
 ↓
FINAL_REVEAL
 ↓
COMPLETED
```

The backend must reject invalid transitions.

For example:

```text
ROUND_1_ACTIVE → ROUND_3_ACTIVE
```

must not be possible.

---

# 10. Shared Database

SQLite is the single source of persistent game data.

## `teams`

```text
id
team_name
member_1_name
member_2_name
current_state

round1_score
round2_score
round3_score
total_score

round1_started_at
round1_completed_at

round2_started_at
round2_completed_at

round3_started_at
round3_completed_at

created_at
updated_at
```

## `team_fragments`

```text
id
team_id
fragment
unlocked_at
```

## `submissions`

```text
id
team_id
round
reference_id
answer
is_correct
points_awarded
submitted_at
```

## `hints`

```text
id
team_id
round
hint_level
points_deducted
created_at
```

## `investments`

```text
id
team_id
option_id
allocation
submitted_at
```

## `game_logs`

```text
id
team_id
event_type
event_data
created_at
```

The schema may be extended when required, but existing shared fields should not be renamed casually.

---

# 11. API Contracts

All player/game communication goes through FastAPI.

## Login

```http
POST /api/auth/login
```

Request:

```json
{
  "team_name": "Team Alpha",
  "member_1_name": "Player 1",
  "member_2_name": "Player 2"
}
```

Response:

```json
{
  "team_id": 1,
  "team_name": "Team Alpha",
  "current_state": "READY"
}
```

## Game State

```http
GET /api/game/state
```

Returns:

* current state
* scores
* current round
* server deadline/timer information
* relevant progression information

## Round 1

```http
GET  /api/round1/items
POST /api/round1/submit
POST /api/round1/complete
```

Backend determines:

* correctness
* points
* fragment unlocks
* valid progression

## Round 2

```http
POST /api/round2/start
GET  /api/round2/files
POST /api/round2/unlock
POST /api/round2/hint
POST /api/round2/chat
GET  /api/round2/conversation
POST /api/round2/complete
```

Backend verifies that the team is allowed to access requested evidence.

## Round 3

```http
GET  /api/round3/options
GET  /api/round3/recommendation
POST /api/round3/invest
POST /api/round3/decision
POST /api/round3/complete
```

The final decision must be validated server-side.

---

# 12. Timer Rules

Timers are **server-authoritative**.

The server stores the actual start/deadline time.

The frontend only displays the countdown.

```text
Round starts
    ↓
Server stores deadline
    ↓
Frontend displays countdown
    ↓
Deadline reached
    ↓
Server rejects late submissions
```

Refreshing the browser must not reset a timer.

The event has an overall target duration of approximately **15–20 minutes**, with the technical specification requiring a **hard 20-minute cap**.

Exact per-round timing must follow the finalized event specification.

---

# 13. Scoring

The event specification defines the scoring logic.

General principles:

### Round 1

Reward:

* accuracy
* speed

### Round 2

Reward:

* correct investigation
* fast solving
* fewer hints

### Round 3

Reward:

* final investment/decision outcome

Overall:

```text
TOTAL SCORE =
ROUND 1
+ ROUND 2
+ ROUND 3
```

The technical specification defines the intended maximum scoring range as:

```text
Round 1: 325
Round 2: 265
Round 3: 200

Maximum Total: 790
```

The exact question-level scoring and penalties must follow the finalized event specification.

Tie-breaking should use server-recorded completion time where required.

---

# 14. Gemini Rules

Gemini is used only for the **Round 2 Assistant**.

The Gemini API key must remain on the backend.

Never expose the API key to the React frontend.

### Gemini can

* explain unlocked evidence
* provide hints
* guide investigation
* answer questions based on available evidence

### Gemini cannot

* unlock files
* change scores
* change state
* submit answers
* reveal locked evidence
* directly reveal Project Omega
* act as the official puzzle validator

### Failure handling

If Gemini fails:

```text
Gemini unavailable
       ↓
Fallback / predefined hint
       ↓
Game continues
```

The event must not depend entirely on live Gemini availability.

---

# 15. Server-Side Reliability

The backend must be authoritative for:

* scores
* answers
* timers
* round progression
* unlocked evidence
* final decisions
* leaderboard

Handle:

* page refresh
* accidental browser closure
* duplicate submissions
* expired timers
* invalid requests
* locked-file access
* Gemini failure
* participant disconnects
* simultaneous teams
* server recovery

A duplicate submission must not award duplicate points.

One team's state must never affect another team's state.

---

# 16. Frontend Structure

```text
frontend/
└── src/
    ├── components/
    │   ├── Timer.jsx
    │   └── ...
    │
    ├── pages/
    │   ├── Login.jsx
    │   ├── Round1.jsx
    │   ├── Round2.jsx
    │   ├── Round3.jsx
    │   └── Completion.jsx
    │
    ├── admin/
    │   ├── AdminLogin.jsx
    │   ├── Dashboard.jsx
    │   ├── Teams.jsx
    │   ├── Logs.jsx
    │   └── Leaderboard.jsx
    │
    ├── services/
    │   └── api.js
    │
    └── App.jsx
```

---

# 17. Backend Structure

```text
backend/
└── app/
    ├── main.py
    │
    ├── routes/
    │   ├── auth.py
    │   ├── game.py
    │   ├── round1.py
    │   ├── round2.py
    │   ├── round3.py
    │   └── admin.py
    │
    ├── services/
    │   ├── game_service.py
    │   ├── scoring_service.py
    │   ├── round1_service.py
    │   ├── round2_service.py
    │   ├── round3_service.py
    │   └── gemini_service.py
    │
    ├── database/
    │   ├── connection.py
    │   └── schema.py
    │
    └── utils/
        ├── timers.py
        └── validation.py
```

Event content should be separated from application logic where practical:

```text
data/
├── round1/
├── round2/
└── round3/
```

This allows questions, clues, evidence and options to be changed without rewriting the application.

---

# 18. UI / Visual Direction

The intended visual identity is:

**futuristic AI terminal + corrupted timeline + glitch aesthetic**

Use:
* white/light text
* futuristic but readable typography
* monospace typography for terminal/data elements
* subtle grid/scanline/glitch effects
* clean cards and panels
* clear timers and progress indicators

Avoid:

* excessive neon
* constant animations
* distracting effects during gameplay
* generic "hacker" visuals
* unnecessary complexity

### Round feel

```text
Round 1 → Futuristic diagnostic/classification system

Round 2 → CHRONOS terminal / digital investigation

Round 3 → High-stakes decision interface

Completion → Mission-complete 
```

---

# 19. GitHub / Collaboration

Use one GitHub repository.

Recommended branches:

```text
main
feature/round1
feature/round2
feature/round3
feature/admin
```

Workflow:

```text
feature branch
     ↓
development
     ↓
local testing
     ↓
Pull Request
     ↓
review
     ↓
main
```

Rules:

* Keep `main` stable.
* Do not directly break shared code.
* Do not change API contracts without coordination.
* Do not rename shared state values casually.
* Reuse existing components/utilities.
* Keep commits focused.
* Test before creating a PR.
* Do not modify another team's round unnecessarily.

Each round team owns the **frontend + backend implementation of its round**.

Shared infrastructure must remain compatible with all rounds.

---

# 20. Vibe-Coding Rules

Before asking Claude to modify the project:

1. Read `PROJECT_REFERENCE.md`.
2. Read the relevant event specification.
3. Inspect existing code before creating files.
4. Reuse existing components and services.
5. Do not rewrite unrelated code.
6. Follow existing API contracts.
7. Follow existing database fields and state names.
8. Make the smallest required change.
9. Test the feature.
10. Check that existing rounds still work.

Claude must not invent:

* new game mechanics
* scoring rules
* narrative facts
* clues
* answers
* state names
* API contracts
* database fields

unless explicitly required by the project specification.

If something is genuinely unspecified, use the **simplest implementation** and do not change the established architecture.

---

# 21. Testing

Before the event, test the complete flow:

```text
Login
 ↓
Round 1
 ↓
Fragments
 ↓
Round 2
 ↓
Omega Discovery
 ↓
Round 3
 ↓
Decision
 ↓
Completion
```

Also test:

* browser refresh
* duplicate submission
* wrong answer
* timer expiry
* direct access to later rounds
* locked evidence access
* Gemini unavailable
* participant disconnect
* simultaneous teams
* server restart/recovery

### Multi-PC Test

Test with the expected number of PCs on the actual LAN.

Verify:

* all PCs connect
* teams remain isolated
* timers remain correct
* scores remain correct
* submissions remain associated with the correct team
* evidence remains team-specific
* leaderboard updates correctly
* admin can monitor all teams

---

# 22. Event-Day Architecture

```text
                 EVENT LAN
                     │
       ┌─────────────┴─────────────┐
       │                           │
 Participant PCs               Admin PC
       │                           │
       └─────────────┬─────────────┘
                     ↓
              CENTRAL SERVER
                     ↓
                  FastAPI
                     ↓
                  SQLite
```

Players connect to the central server through its LAN address.

Example:

```text
http://192.168.x.x:<port>
```

The actual address and port are determined during deployment.

Before the event:

* test the actual LAN
* test all PCs
* verify database
* verify event data
* verify Gemini configuration
* verify admin access
* create a database backup
* perform a complete rehearsal

Do not make major architecture changes on event day.

---

# 23. Source of Truth

Use the documents in this order:

```text
FINAL EVENT REQUIREMENTS
        ↓
EVENT SPECIFICATION
        ↓
PROJECT_REFERENCE.md
        ↓
EXISTING WORKING CODE
        ↓
ORIGINAL TECHNICAL SPECIFICATION
```

The **Event Guide / Event Specification** defines what the game should be.

This file defines how the agreed simplified architecture should implement it.

The original Technical Specification is a reference for reliability and intended behaviour. Its original technology choices should **not** be copied if they conflict with the agreed React + FastAPI + SQLite architecture.

---

# 24. Core Principle

The goal is not to build the most complicated system.

The goal is to build a reliable event:

```text
~20-25 Player PCs
       ↓
One Central LAN Server
       ↓
One Shared Database
       ↓
Three Connected Rounds
       ↓
Admin Monitoring
       ↓
Leaderboard
       ↓
Successful Event
```

**Build simple → Integrate carefully → Test heavily → Polish last.**