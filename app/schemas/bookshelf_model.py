from enum import Enum
from pydantic import BaseModel

class Status(Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    DID_NOT_COMPLETE = "did_not_complete"
    COMPLETED = "completed"


