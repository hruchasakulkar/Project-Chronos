from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ..services.gemini_service import ask_gemini
from ..services.round2_service import (
    get_team_case,
    get_team_evidence,
    get_files_for_team,
    get_file_by_id,
    get_team_suspects,
    get_team_state,
    start_round2 as start_round2_service,
    reserve_ai_question,
    save_ai_response,
    get_conversation,
    complete_round2 as complete_round2_service,
)


router = APIRouter(
    prefix="/api/round2",
    tags=["Round 2"]
)


class AIQuestionRequest(BaseModel):
    team_id: int = Field(..., ge=1)
    message: str = Field(..., min_length=1, max_length=500)


def _require_team(team_id: int):
    state = get_team_state(team_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )

    return state


@router.post("/start")
def start_round2(team_id: int):
    case = get_team_case(team_id)

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found or no Round 2 case available."
        )

    state = get_team_state(team_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found."
        )

    result = start_round2_service(team_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found."
        )

    if not result["success"]:
        raise HTTPException(
            status_code=409,
            detail=result["error"]
        )

    return {
        "team_id": team_id,
        "team_name": state["team_name"],
        "state": "ROUND_2_ACTIVE",
        "case_id": case["case_id"],
        "case_code": case["case_code"],
        "incident": case["incident"],
        "r2_start_time": result["r2_start_time"],
        "r2_end_time": result["r2_end_time"],
        "ai_questions_used": state["ai_questions_used"],
        "ai_questions_remaining": state["ai_questions_remaining"],
        "ai_points_remaining": state["ai_points_remaining"],
    }


@router.get("/progress")
def get_progress(team_id: int):
    state = get_team_state(team_id)

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="Team not found."
        )

    case = get_team_case(team_id)

    return {
    "team_id": team_id,
    "team_name": state["team_name"],
    "state": state["current_state"],
    "case_id": case["case_id"] if case else None,
    "case_code": case["case_code"] if case else None,
    "r2_start_time": state["r2_start_time"],
    "r2_end_time": state["r2_end_time"],
    "ai_questions_used": state["ai_questions_used"],
    "ai_questions_remaining": state["ai_questions_remaining"],
    "ai_points_remaining": state["ai_points_remaining"],
}


@router.get("/files")
def get_files(team_id: int = Query(..., ge=1)):
    _require_team(team_id)

    return get_files_for_team(team_id)


@router.get("/files/{file_id}")
def get_file(
    file_id: str,
    team_id: int = Query(..., ge=1)
):
    _require_team(team_id)

    file = get_file_by_id(file_id, team_id)

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )

    return file


@router.get("/suspects")
def get_suspects(team_id: int = Query(..., ge=1)):
    _require_team(team_id)

    suspects = get_team_suspects(team_id)

    return [
        {
            "name": suspect["suspect_name"],
            "user_id": suspect["user_id"],
        }
        for suspect in suspects
    ]


@router.get("/ai/status")
def ai_status(team_id: int = Query(..., ge=1)):
    state = _require_team(team_id)

    return {
        "team_id": team_id,
        "questions_used": state["ai_questions_used"],
        "questions_remaining": state["ai_questions_remaining"],
        "ai_points_remaining": state["ai_points_remaining"],
    }


@router.post("/chat")
async def chat(body: AIQuestionRequest):
    state = _require_team(body.team_id)

    question = body.message.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "empty_question",
                "message": "Question cannot be blank."
            }
        )

    evidence = get_team_evidence(body.team_id)

    if not evidence:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "evidence_locked",
                "message": "Round 2 evidence is not available."
            }
        )

    # reserve the AI question and calculate its cost
    reservation = reserve_ai_question(body.team_id)

    if reservation is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "team_not_found",
                "message": "Team not found."
            }
        )

    if not reservation["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "ai_limit_reached",
                "message": reservation["reason"],
                "questions_remaining": max(
                    0,
                    3 - state["ai_questions_used"]
                ),
                "ai_points_remaining": state["ai_points_remaining"],
            }
        )

    question_number = reservation["question_number"]
    points_charged = reservation["points_deducted"]
    points_remaining = reservation["points_remaining"]

    case = get_team_case(body.team_id)

    answer, used_fallback = await ask_gemini(
        question,
        evidence,
        case["culprit"] if case else None,
    )

    # store the actual points charged, not whether fallback was used
    save_ai_response(
        body.team_id,
        question_number,
        question,
        answer,
        points_charged,
    )

    return {
        "reply": answer,
        "answer": answer,
        "question_number": question_number,
        "points_deducted": points_charged,
        "ai_points_remaining": points_remaining,
        "progress": {
            "questions_used": question_number,
            "questions_remaining": max(
                0,
                3 - question_number
            ),
            "ai_points_remaining": points_remaining,
        },
    }


@router.post("/ai/ask")
async def ai_ask(body: AIQuestionRequest):
    """
    Compatibility endpoint for clients using the /ai/ask contract.
    """
    return await chat(body)


@router.get("/conversation")
def conversation(team_id: int = Query(..., ge=1)):
    _require_team(team_id)

    return get_conversation(team_id)


@router.post("/complete")
def complete(team_id: int = Query(..., ge=1)):
    _require_team(team_id)
    result = complete_round2_service(team_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Team not found.")

    if not result["success"]:
        raise HTTPException(status_code=409, detail=result["error"])

    return {
        "team_id": team_id,
        "completed": True,
        "state": "ROUND_2_COMPLETED",
        "already_completed": result.get("already_completed", False),
    }
