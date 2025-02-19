from fastapi import Depends
from ..repos.notes_repo import NotesRepo
from ..models import NotesCreate

class NotesService:
    def __init__(self, repo: NotesRepo = Depends()):
        self.repo = repo
    
    async def create_order(self, order: NotesCreate):
        # Business logic, validation, etc.
        return await self.repo.create(order)