import uuid
from sqlalchemy.dialects.postgresql import UUID
from database import Base
from sqlalchemy import String, Integer, Column, Text, ForeignKey,DateTime
from datetime import datetime,timedelta
from sqlalchemy.orm import relationship,backref


class Admin(Base):
    __tablename__="Admin"
    id= Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    name=Column(String)


class Users(Base):
    __tablename__ = "User"
    id = Column(UUID(as_uuid=True), primary_key=True,index= True,default=uuid.uuid4)
    fullname=Column(String,nullable=False)
    username=Column(String)
    telephone = Column(String)
    email = Column(String)
    password = Column(String)
    created_on= Column(DateTime,default=datetime.utcnow)
    created_by= Column(String)
    updated_on=Column(DateTime,onupdate=datetime.utcnow)
    updated_by=Column(String)
    reviews=relationship("review",backref=backref('user'))
    address=relationship("User_address",backref=backref("user"))
    orders=relationship("Order",backref=backref("user"))


class User_address(Base):
    __tablename__ = "address"
    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("User.id"))
    address_line1 = Column(String)
    address_line2 = Column(String)
    city = Column(String)
    postal_code = Column(Integer)
    country = Column(String)


class Product(Base):
    __tablename__ = "product"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    name = Column(String)
    SKU = Column(String)
    category_id = Column(UUID(as_uuid=True), ForeignKey("category.id"),default=uuid.uuid4)
    price = Column(Integer)
    reviews = relationship("review", backref=backref('product'))


class Product_category(Base):
    __tablename__ = "category"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    products = relationship("Product", backref=backref("category"))


class Order(Base):
    __tablename__ = "order"
    order_id = Column(UUID(as_uuid=True), primary_key=True,unique=True,default=uuid.uuid4)
    user_id= Column(UUID(as_uuid=True),ForeignKey("User.id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"))
    ordered_date=Column(DateTime,default=datetime.utcnow)
    delivery_date = Column(DateTime)
    address_id= Column(UUID(as_uuid=True),ForeignKey("address.id"))
    products=relationship("Product",backref=backref("order"))
    address=relationship("User_address",backref=backref("order"))


class review(Base):
    __tablename__ = "review"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    prod_id = Column(UUID(as_uuid=True), ForeignKey("product.id"))
    comment = Column(Text)
    rating = Column(Integer)
    user_id = Column(UUID(as_uuid=True), ForeignKey("User.id"))

