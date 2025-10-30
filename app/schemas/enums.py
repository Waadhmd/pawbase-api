from enum import Enum as PyEnum

#ENUM DEFINITIONS
class UserRole(str, PyEnum):
    #SYSTEM_ADMIN = "system_admin"
    ORG_ADMIN = "org_admin"
    STAFF = "staff"
    ADOPTER = "adopter"

class AdoptionStatus(str, PyEnum):
    available = "Available"
    pending = "Pending"
    adopted = "Adopted"
    quarantine = "Quarantine"

class RequestStatus(str, PyEnum):
    submitted = "Submitted"
    approved = "Approved"
    rejected = "Rejected"