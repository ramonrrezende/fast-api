
from pydantic import BaseModel


class UserEnroll(BaseModel):
    id: int
    course_id: int
    user_id: int
