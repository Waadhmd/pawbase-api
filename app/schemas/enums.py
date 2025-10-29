from enum import Enum as PyEnum

#ENUM DEFINITIONS
class AdoptionStatus(str, PyEnum):
    available = "Available"
    pending = "Pending"
    adopted = "Adopted"
    quarantine = "Quarantine"

class RequestStatus(str, PyEnum):
    submitted = "Submitted"
    approved = "Approved"
    rejected = "Rejected"