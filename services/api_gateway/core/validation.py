"""数据验证模块"""
from typing import Any, Dict
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError

def validate_request_data(data: Dict[str, Any], model: BaseModel) -> BaseModel:
    """验证请求数据"""
    try:
        return model(**data)
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        ) 