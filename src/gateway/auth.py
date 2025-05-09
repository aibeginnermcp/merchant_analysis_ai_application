"""
认证模块
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.shared.config import settings

class Token(BaseModel):
    """Token模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token数据模型"""
    merchant_id: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    """用户模型"""
    merchant_id: str
    username: str
    disabled: bool = False
    scopes: list[str] = []

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 验证结果
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希值
    
    Args:
        password: 明文密码
        
    Returns:
        str: 密码哈希值
    """
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌
    
    Args:
        data: Token数据
        expires_delta: 过期时间
        
    Returns:
        str: JWT Token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """获取当前用户
    
    Args:
        token: JWT Token
        
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: 认证失败
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        merchant_id: str = payload.get("sub")
        if merchant_id is None:
            raise credentials_exception
        token_data = TokenData(merchant_id=merchant_id)
    except JWTError:
        raise credentials_exception
        
    # 这里应该从数据库获取用户信息
    user = User(
        merchant_id=token_data.merchant_id,
        username=f"merchant_{token_data.merchant_id}",
        scopes=["merchant"]
    )
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 用户对象
        
    Raises:
        HTTPException: 用户已禁用
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="用户已禁用")
    return current_user 