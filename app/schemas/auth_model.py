from pydantic import BaseModel

class UserProfile(BaseModel):
    user_id: str
    first_name: str
    last_name: str 