from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends

secretkey = "g7dbriu2y98373ehwbd8wtbf3w8e7897287dfghj234567"
algorithm = "HS256"
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")


def createAccessToken(data: dict):
    datatoencode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    datatoencode.update({"exp": expire})
    accesstoken = jwt.encode(datatoencode, secretkey, algorithm=algorithm)
    return accesstoken


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, secretkey, algorithms=[algorithm])
        print(payload)
        username: int = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    return


def get_current_user(data: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return verify_token(data, credentials_exception)
