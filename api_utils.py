from typing import Optional
from pydantic import BaseModel


class UserRequest(BaseModel):
    username: str
    password: str
    role: str


class UserUpdatePassword(BaseModel):
    password: str


class UserDeposit(BaseModel):
    deposit: int


class UserBuyProduct(BaseModel):
    productId: str
    no_of_products: int


class NewProductRequest(BaseModel):
    productName: str
    cost: int
    amountAvailable: int


class ProductUpdate(BaseModel):
    productName: str
    cost: Optional[int] = None
    amountAvailable: Optional[int] = None


class ProductDelete(BaseModel):
    productName: str