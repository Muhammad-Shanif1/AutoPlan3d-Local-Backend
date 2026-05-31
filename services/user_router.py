from fastapi import APIRouter, status, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from schema.user import UserCreateSchema, UserResponseSchema, LoginSchema, UserLoginResponseSchema, ContinueWithGoogleSchema, UserUpdateSchema
from services.models import UserModel
import services.controller as controller
import services.send_email
import services.signIn_with_google
from services.db import get_db

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserLoginResponseSchema)
def register_endpoint(user: UserCreateSchema, db: Session = Depends(get_db)):
	return controller.register(user, db)


@router.post("/login_with_google", status_code=status.HTTP_200_OK, response_model=UserLoginResponseSchema)
async def login_with_google_endpoint(user: ContinueWithGoogleSchema, db: Session = Depends(get_db)):
	return await services.signIn_with_google.login_with_google(user, db)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponseSchema)
def login_endpoint(user: LoginSchema, db: Session = Depends(get_db)):
	return controller.login(user, db)


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout_endpoint():
	return controller.logout()


@router.post("/is-authenticat", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def is_authenticat_endpoint(request: Request, db: Session = Depends(get_db)):
	return controller.is_authenticated(request, db)


@router.post("/forget-password", status_code=status.HTTP_200_OK)
def send_otp_endpoint(
	email: str,
	background_tasks: BackgroundTasks,
	db: Session = Depends(get_db),
):
	user = db.query(UserModel).filter(UserModel.email == email).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")

	otp_response = services.send_email.send_otp_email(
		email_to=email,
		background_tasks=background_tasks,
	)

	# Save OTP to database
	controller.save_otp(email, otp_response["otp"], db)

	# Do NOT return OTP to client in production, but for now we'll keep it for debugging or remove it.
	# The user asked to fix the partial bug (sending OTP to client), so I will remove it from response.
	return {"message": "OTP sent successfully", "user_id": user.id}


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp_endpoint(
	email: str,
	otp: str,
	db: Session = Depends(get_db),
):
	return controller.verify_otp(email, otp, db)


@router.put("/update-password", status_code=status.HTTP_200_OK)
def update_password_endpoint(
	user_id: int,
	new_password: str,
	db: Session = Depends(get_db),
):
	return controller.update_password(user_id, new_password, db)


@router.get("/get_user_info/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.get_user(user_id, db)


@router.put("/update_user_info/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def update_user_info_endpoint(user_id: int, body: UserUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.update_user_info(user_id, body, db)


@router.delete("/remove_user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_endpoint(user_id: int, password: str, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.delete_user(user_id, password, db)



