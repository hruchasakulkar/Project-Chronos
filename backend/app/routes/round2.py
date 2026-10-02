from fastapi import APIRouter, HTTPException

from ..services.round2_service import (
    get_files_for_team,
    get_file_by_id
)


router = APIRouter(
    prefix="/api/round2",
    tags=["Round 2"]
)


@router.get("/files")
def get_files(team_id: int):
    return get_files_for_team(team_id)


@router.get("/files/{file_id}")
def get_file(file_id: str, team_id: int):
    file = get_file_by_id(file_id, team_id)

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found or access denied"
        )

    return file