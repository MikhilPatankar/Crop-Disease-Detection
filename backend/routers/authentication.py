from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from .. import auth, schemas
from ..database import get_db

router = APIRouter(
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def register(user: schemas.UserCreate, db: AsyncIOMotorDatabase = Depends(get_db)):
    """Registers a new user."""
    db_user = await db.users.find_one({"username": user.username})
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    hashed_password = auth.get_password_hash(user.password)
    user_doc = {"username": user.username, "password": hashed_password}
    result = await db.users.insert_one(user_doc)
    new_user = await db.users.find_one({"_id": result.inserted_id})
    return schemas.User.model_validate(new_user)

@router.post("/login", response_model=schemas.Token)
async def login(
    user_credentials: schemas.UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Logs in a user and returns a JWT token."""
    user = await auth.authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=schemas.User)
async def profile(current_user: schemas.User = Depends(auth.get_current_user)):
    """A protected route to get user profile information."""
    return current_user

