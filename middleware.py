from fastapi import Request, HTTPException
from firebase_admin import auth
from firebase_config import db
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude public paths
        public_paths = ["/", "/docs", "/openapi.json", "/redoc"]
        if request.url.path in public_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = auth_header.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
            uid = decoded_token['uid']
            
            # Fetch user from Firestore
            user_doc = db.collection('users').document(uid).get()
            if not user_doc.exists:
                raise HTTPException(status_code=404, detail="User not found in system")
            
            user_data = user_doc.to_dict()
            request.state.user = {
                "uid": uid,
                "email": user_data.get("email"),
                "companyId": user_data.get("company_id") or user_data.get("companyId"),
                "role": user_data.get("role")
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

        response = await call_next(request)
        return response
