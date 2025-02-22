from fastapi import Depends
from ..repos.notes_repo import NotesRepo
from ..models import NoteCreate

class NotesService:
    def __init__(self, repo: NotesRepo = Depends()):
        self.repo = repo
    
    async def create_order(self, order: NoteCreate):
        # Business logic, validation, etc.
        return await self.repo.create(order)