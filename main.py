from fastapi import FastAPI, Request, HTTPException, Depends
from firebase_admin import auth, firestore
from firebase_config import db
from models import CreateCompanyRequest, CreateUserRequest
from datetime import datetime
import uuid

from middleware import AuthMiddleware

app = FastAPI(title="LaborDesk Backend API")
app.add_middleware(AuthMiddleware)

# Helper for Company Admin access control
def get_current_company_admin(request: Request):
    user = request.state.user
    if user['role'] not in ['admin', 'companyAdmin']:
        raise HTTPException(status_code=403, detail="Only Company Admins can perform this action")
    return user

# Helper for Super Admin access control
def get_current_super_admin(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
         raise HTTPException(status_code=401, detail="Authentication required")
    # Note: In production, this email should be in a secure config/env
    super_admin_emails = ["admin@acodr.com", "super@labordesk.com"]
    if user['email'] not in super_admin_emails:
        raise HTTPException(status_code=403, detail="Only Super Admins can perform this action")
    return user

@app.post("/create-company")
async def create_company(req: CreateCompanyRequest, request: Request):
    """Creates a new company and its first admin user. Allows public access for initiation."""
    print(f"[BACKEND] Creating company: {req.company_name} for admin: {req.admin_email}")
    try:
        # 1. Create Firebase Auth user for the Company Admin
        firebase_user = auth.create_user(
            email=req.admin_email,
            password=req.admin_password,
            display_name=req.admin_name
        )
        uid = firebase_user.uid
        print(f"[BACKEND] Created Firebase User: {uid}")
        
        # 2. Create Company document
        company_id = str(uuid.uuid4())
        company_ref = db.collection('companies').document(company_id)
        
        company_data = {
            "name": req.company_name,
            "email": req.company_email,
            "address": {
                "street": req.street_address,
                "city": req.city,
                "state": req.state,
                "zip": req.zip_code,
                "landmark": req.landmark
            },
            "phone": req.company_phone,
            "adminName": req.admin_name,
            "adminEmail": req.admin_email, # Business email for profile
            "adminPhone": req.admin_phone,
            "orgAdminUserId": uid,
            "isActive": True,
            "industry": req.industry,
            "createdAt": firestore.SERVER_TIMESTAMP
        }
        company_ref.set(company_data)
        print(f"[BACKEND] Created Company record: {company_id}")
        
        # 3. Create User document for the Company Admin
        user_ref = db.collection('users').document(uid)
        user_data = {
            "name": req.admin_name,
            "email": req.company_email, # Using official email as requested
            "phone": req.admin_phone, # Administrative phone
            "orgId": company_id,
            "role": "admin", # Mapping to UserRole.companyAdmin
            "isActive": True,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "createdBy": "system_init"
        }
        user_ref.set(user_data)
        print(f"[BACKEND] Created Admin Profile and linked to company.")
        
        return {
            "status": "success",
            "orgId": company_id,
            "admin_uid": uid
        }
    except auth.EmailAlreadyExistsError:
        print(f"[BACKEND] Error: Email already exists.")
        raise HTTPException(status_code=400, detail="Admin email already exists")
    except Exception as e:
        print(f"[BACKEND] Fatal Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-user")
async def create_company_user(req: CreateUserRequest, admin = Depends(get_current_company_admin)):
    """Creates a new user inside the same company as the admin. Company Admin only."""
    try:
        # Check global email uniqueness (handled by Firebase Auth automatically)
        firebase_user = auth.create_user(
            email=req.email,
            password=req.password,
            display_name=req.name,
            phone_number=req.phone if req.phone.startswith("+") else f"+91{req.phone}"
        )
        uid = firebase_user.uid
        
        # Create Firestore User record
        user_ref = db.collection('users').document(uid)
        user_data = {
            "name": req.name,
            "email": req.email,
            "phone": req.phone,
            "orgId": admin['orgId'], # Using new naming convention
            "role": "user", # Mapping to UserRole.companyUser
            "isActive": True,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "createdBy": admin['uid']
        }
        user_ref.set(user_data)
        
        return {
            "status": "success",
            "uid": uid,
            "orgId": admin['orgId']
        }
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User email already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/me")
async def get_my_profile(request: Request):
    """Returns the authenticated user context."""
    return request.state.user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
