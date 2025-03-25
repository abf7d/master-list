from pydantic import BaseModel
from typing import Any, Dict, Optional, List, Union

class ErrorDetail(BaseModel):
    loc: Optional[List[str]] = None
    msg: str
    type: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    errors: Optional[List[ErrorDetail]] = None

