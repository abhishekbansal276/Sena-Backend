from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateCompanyRequest(BaseModel):
    company_name: str
    company_email: EmailStr
    admin_name: str
    admin_email: EmailStr
    admin_password: str
    industry: Optional[str] = "General"

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: Optional[str] = "user" # Matches companyUser mapping
