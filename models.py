from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateCompanyRequest(BaseModel):
    company_name: str
    company_email: EmailStr
    street_address: str
    city: str
    state: str
    zip_code: str
    landmark: Optional[str] = None
    company_phone: Optional[str] = None
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    admin_phone: Optional[str] = None # Added for direct admin contact
    industry: Optional[str] = "General"

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: Optional[str] = "user" # Matches companyUser mapping
