from datetime import date
from uuid import UUID,uuid4
from pydantic import BaseModel,Field
class UserInfoBase(BaseModel):
    username: str
    fullname: str
    email: str
    telephone: str
    class Config:
        orm_mode = True


class UserInfo(UserInfoBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True


class UserCreate(UserInfoBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str

class AddCateg(BaseModel):
    name:str
    description:str


class ProductCategory(AddCateg):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True


class AddProduct(BaseModel):
    name: str
    SKU: str
    price: int
    category:str

    class Config:
        orm_mode = True


class prod(AddProduct):
    id: UUID = Field(default_factory=uuid4)
    category:ProductCategory

    class Config:
        orm_mode = True


class UpdateProduct(BaseModel):
    price:int


class AddAddress(BaseModel):
    # userid:UUID = Field(default_factory=uuid4)
    address_line1:str
    address_line2:str
    city:str
    postal_code:int
    country:str


class PlaceOrder(BaseModel):
    product_name:str
    class Config:
        orm_mode = True


class Ordered(PlaceOrder):
    order_id:UUID=Field(default_factory=uuid4)

    class Config:
        orm_mode = True


class Get_prod_by_cat(BaseModel):
    name:str
    price:int
    class Config:
        orm_mode = True


class addreview(BaseModel):
    productname:str
    comment:str
    rating:int

    class Config:
        orm_mode = True
class get_reviews_by_name(BaseModel):
    productname: str

    class Config:
        orm_mode = True
