from fastapi import HTTPException, status, Depends, Request
from schema.project import ProjectSchema
from sqlalchemy.orm import Session
from services.models import UserModel
from schema.user import UserCreateSchema, LoginSchema
from passlib.context import CryptContext
from services.settings import settings
from datetime import datetime, timedelta
from services.db import get_db
import jwt
import secrets
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def register(body: UserCreateSchema, db: Session):
    is_user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if is_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    hash_password = get_password_hash(body.password)

    new_user = UserModel(
        name=body.name,
        password=hash_password,
        email=body.email,
        phone=body.phone,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"user": new_user, "token": create_access_token(new_user)}



def login(body: LoginSchema, db: Session):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please create an account first."
        )

    if not verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return {"user": user, "token": create_access_token(user)}


def is_authenticated(request: Request, db: Session = Depends(get_db)):

    try:
        token = request.headers.get("authorization")

        if not token: 
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")


        token=token.split(" ")[-1]   # is header= jwt token
        data=jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        user_id=data.get("_id")

        # this is not required because jwt.decode will raise an exception if the token is expired
        # exp_time=int(data.get("exp"))
        # if datetime.now().timestamp() > exp_time:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        
        user=db.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="you are not authenticated")

        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def create_access_token(user: UserModel) -> str:
    expire_time = datetime.utcnow() + timedelta(minutes=settings.EXPIRE_MINUTES)
    return jwt.encode(
        {"_id": user.id, "email": user.email, "exp": expire_time.timestamp()},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def update_password(user_id: int, new_password: str, db: Session):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.password = get_password_hash(new_password)
    # Clear OTP after successful reset
    user.otp = None
    user.otp_expiry = None
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}


def save_otp(email: str, otp: str, db: Session):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    return user


def verify_otp(email: str, otp: str, db: Session):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.otp or user.otp != otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    if datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP has expired")

    return {"message": "OTP verified successfully", "user_id": user.id}


def update_user_info(user_id: int, body, db: Session):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if body.name is not None:
        user.name = body.name
    if body.email is not None:
        # Check if email is already taken by another user
        if body.email != user.email:
            is_email_taken = db.query(UserModel).filter(UserModel.email == body.email).first()
            if is_email_taken:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken")
        user.email = body.email
    if body.phone is not None:
        user.phone = body.phone

    db.commit()
    db.refresh(user)
    return user


def get_user(user_id: int, db: Session):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def logout():
    """
    Instructs the client to delete the JWT token. For stateless JWT, logout is handled on the client side.
    """
    return {"message": "Successfully logged out. Please delete the token on the client side."}


def continue_with_google(body, db: Session):
    """Handle Google sign-in: create user if doesn't exist, return JWT token."""
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    
    if user:
        # User exists, generate token and return
        return {"user": user, "token": create_access_token(user)}
    
    # Create new user from Google data
    generated_password = secrets.token_urlsafe(32)
    new_user = UserModel(
        name=body.name or body.email.split("@")[0],
        password=get_password_hash(generated_password),
        email=body.email,
        phone="",
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"user": new_user, "token": create_access_token(new_user)}

def delete_user(user_id: int, password: str, db: Session):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}







def create_project(user_id: int, project: ProjectSchema, db: Session):
    from services.models import ProjectModel  # Import here to avoid circular import

    new_project = ProjectModel(
        title=project.title,
        description=project.description,
        project_data=project.project_data,
        user_id=user_id
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project



def get_projects(user_id: int, db: Session):
    from services.models import ProjectModel  # Import here to avoid circular import

    projects = db.query(ProjectModel).filter(ProjectModel.user_id == user_id).all()
    # total_projects=len([p.project_id for p in projects])
    return projects

def delete_project(project_id: int, password: str, current_user_id: int, db: Session):
    # First verify the password of the current user
    user = db.query(UserModel).filter(UserModel.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    from services.models import ProjectModel  # Import here to avoid circular import
    project = db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


def update_project(project_id: int, project: ProjectSchema, current_user_id: int, db: Session):
    from services.models import ProjectModel  # Import here to avoid circular import

    existing_project = db.query(ProjectModel).filter(ProjectModel.project_id == project_id).first()
    if not existing_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if existing_project.user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    existing_project.title = project.title
    existing_project.description = project.description
    if project.project_data is not None:
        existing_project.project_data = project.project_data
    
    db.commit()
    db.refresh(existing_project)
    return existing_project


# Alias for backward compatibility with older imports
is_authenticat = is_authenticated

