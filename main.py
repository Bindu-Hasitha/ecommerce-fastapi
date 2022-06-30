import datetime
from fastapi import FastAPI, Depends, HTTPException, status
import model
import schema
from database import SessionLocal
from sqlalchemy.orm import Session
import hashing
from fastapi.security import OAuth2PasswordRequestForm
import auth
import pickle
from jose import jwt
from typing import List
import logging


logger= logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter=logging.Formatter('%(levelname)s:%(name)s:%(message)s')
file_handler= logging.FileHandler('main.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


app = FastAPI()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.post("/login", tags=["User"])
def login_user(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(model.Users).filter(model.Users.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credential")

    if not hashing.verify(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password")
    accesstoken = auth.createAccessToken({"id": user.username})
    #save variable
    pickle.dump(accesstoken,open("accesstoken.dat","wb"))

    return {"access_token": accesstoken, "token_type": "bearer"}


@app.post("/createUser", tags=["User"], response_model=schema.UserInfo)
def create_user(user: schema.UserCreate, db: Session = Depends(get_db)):
    logger.info("creating user")
    hashed_password = hashing.bcrypt(user.password)
    new_user = model.Users(
        username=user.username.lower(),
        fullname=user.fullname,
        email=user.email,
        telephone=user.telephone,
        password=hashed_password,
        created_by=user.username
    )
    db_user=db.query(model.Users).filter(model.Users.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="username already exixts")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"created {new_user.username} successfully")
    return new_user


@app.post("/addAddress",tags=["User"])
def addAddress(address:schema.AddAddress,db:Session=Depends(get_db)):

    #getting current user
    access_token=pickle.load(open("accesstoken.dat","rb"))
    current_user= jwt.decode(access_token,key="g7dbriu2y98373ehwbd8wtbf3w8e7897287dfghj234567")
    user=db.query(model.Users).filter(model.Users.username==current_user["id"]).first()
    user_address=model.User_address(
        user=user,
        address_line1=address.address_line1,
        address_line2=address.address_line2,
        city=address.city,
        postal_code=address.postal_code,
        country=address.country
    )
    db.add(user_address)
    db.commit()
    db.refresh(user_address)
    logger.info("added address successfully")
    return user_address


@app.get("/getUser/{id}", tags=["Admin"], response_model=schema.UserInfoBase)
def get_user_by_id(id, db: Session = Depends(get_db), current_user:schema.UserCreate=Depends(auth.get_current_user)):
    return db.query(model.Users).filter(model.Users.id == id).first()


@app.get("/getUser/username/{username}", tags=["Admin"], response_model=schema.UserInfoBase)
def get_user_by_username(username, db: Session = Depends(get_db)):
    db_user = db.query(model.Users).filter(model.Users.username == username).first()
    return db_user


@app.get("/getAllUsers", tags=["Admin"], response_model=schema.UserInfoBase)
def get_all_user(db: Session = Depends(get_db)):
    return db.query(model.Users).all()


@app.put("/updateUser/{username}", tags=["User"], response_model=schema.UserInfo)
def update_user(username, user: schema.UserInfoBase, db: Session = Depends(get_db)):
    logger.info("updating user details")
    user_to_be_updated = db.query(model.Users).filter(model.Users.username == username).first()
    user_to_be_updated.fullname = user.fullname
    user_to_be_updated.username = user.username
    user_to_be_updated.email = user.email
    user_to_be_updated.telephone = user.telephone
    user_to_be_updated.updated_by=user.username
    db.commit()
    logger.info(f"updated {user_to_be_updated.username} successfully")
    return user_to_be_updated


@app.delete("/deleteUser/username", tags=["User"])
def delete_user(username, db: Session = Depends(get_db)):
    user_to_be_deleted = db.query(model.Users).filter(model.Users.username == username).first()

    if user_to_be_deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found")

    db.delete(user_to_be_deleted)
    db.commit()

    return user_to_be_deleted


@app.post("/addCategory", tags=["Category"])
def add_category(categ: schema.AddCateg, db: Session = Depends(get_db)):
    category = model.Product_category(
        name=categ.name,
        description=categ.description

    )
    db.add(category)
    db.commit()
    db.refresh(category)
    logger.info(f"added {category.name} successfully")
    return category


@app.get("/getCategory/{name}",tags=["Category"], response_model=schema.ProductCategory)
def get_category_by_name(name, db: Session = Depends(get_db)):
    get_category = db.query(model.Product_category).filter(model.Product_category.name == name).first()

    if get_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category Not Found")

    return get_category


@app.get("/getAllCategory", tags=["Category"])
def get_all_category(db: Session = Depends(get_db)):
    get_all = db.query(model.Product_category).all()
    return get_all


@app.put("/updateCategory/{id}", tags=["Category"], response_model=schema.ProductCategory)
def update_category(id, categ: schema.ProductCategory, db: Session = Depends(get_db)):
    categ_to_update = db.query(model.Product_category).filter(model.Product_category.id == id).first()
    categ_to_update.id = categ.id
    categ_to_update.name = categ.name
    categ_to_update.description = categ.description

    db.commit()
    logger.info(f"updated {categ_to_update.name} successfully")
    return categ_to_update


@app.post("/addProduct", tags=["Admin"],response_model=schema.prod)
def add_product(product: schema.AddProduct, db: Session = Depends(get_db)):
    catObj=db.query(model.Product_category).filter(model.Product_category.name==product.category).first()

    new_product = model.Product(
        name=product.name,
        SKU=product.SKU,
        price=product.price,
        category=catObj

    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    logger.info(f"added {new_product.name} successfully")
    return new_product


@app.get("/getProduct/{name}", tags=["Products"])
def get_product_by_id(name,db:Session=Depends(get_db)):
    get_product=db.query(model.Product).filter(model.Product.name==name).first()

    if get_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")

    return get_product


@app.get("/getProductByCateg/{name}", tags=["Products"],response_model=List[schema.Get_prod_by_cat])
def get_product_by_categ(name,db:Session=Depends(get_db)):
    catObj=db.query(model.Product_category).filter(model.Product_category.name==name).first()

    return catObj.products


@app.put("/updateProduct/{name}", tags=["Admin"])
def update_product(name,prod:schema.UpdateProduct,db:Session=Depends(get_db)):
    prod_to_be_updated= db.query(model.Product).filter(model.Product.name==name).first()
    prod_to_be_updated.price= prod.price

    db.commit()
    logger.info(f"updated successfully")
    return "updated successfully"


@app.delete("/deleteProduct/{id}", tags=["Admin"])
def delete_product(id,db:Session=Depends(get_db)):
    prod_to_deleted= db.query(model.Product).filter(model.Product.id==id)

    db.delete(prod_to_deleted)
    db.commit()

    return prod_to_deleted


@app.get("/getAllOrders/{username}", tags=["Orders"])
def get_all_orders(username,db:Session=Depends(get_db)):
    user_= db.query(model.Users).filter(model.Users.username==username).first()

    return user_.orders


@app.post("/placeOrder", tags=["Orders"])
def place_order(order:schema.PlaceOrder,db:Session=Depends(get_db)):
    access_token = pickle.load(open("accesstoken.dat", "rb"))
    current_user = jwt.decode(access_token, key="g7dbriu2y98373ehwbd8wtbf3w8e7897287dfghj234567")
    user3 = db.query(model.Users).filter(model.Users.username == current_user["id"]).first()
    today=datetime.datetime.utcnow()

    product_obj=db.query(model.Product).filter(model.Product.name==order.product_name).first()

    order_= model.Order(
        user=user3,
        products= product_obj,
        ordered_date=today,
        delivery_date=today+datetime.timedelta(days=2),
        address=user3.address[0]
    )
    db.add(order_)
    db.commit()
    db.refresh((order_))
    logger.info("ordered placed successfully")
    return (order_)


@app.post("/review/{product_name}", tags=["Reviews"])
def add_review(request:schema.addreview,db:Session=Depends(get_db)):
    access_token = pickle.load(open("accesstoken.dat", "rb"))
    current_user = jwt.decode(access_token, key="g7dbriu2y98373ehwbd8wtbf3w8e7897287dfghj234567")
    user3 = db.query(model.Users).filter(model.Users.username == current_user["id"]).first()
    prod= db.query(model.Product).filter(model.Product.name==request.productname).first()
    review= model.review(
        user= user3,
        product=prod,
        comment= request.comment,
        rating=request.rating,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(f"review added successfully for {review.prod_id}")
    return review

@app.get("/getAllReviews/{name}", tags=["Reviews"])
def get_all_reviews(name,db:Session=Depends(get_db)):
    product = db.query(model.Product).filter(model.Product.name==name).first()
    reviews=product.reviews
    return reviews
