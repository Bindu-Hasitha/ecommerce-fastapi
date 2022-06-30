import unittest
from fastapi.testclient import TestClient
from main import app

client=TestClient(app=app)

data={
  "username": "username7",
  "fullname": "user",
  "email": "user@gmail.com",
  "telephone": "456781234",
  "password": "password"
}

address_data={
  "address_line1": "address_line1",
  "address_line2": "address_line2",
  "city": "city",
  "postal_code": 0,
  "country": "country"
}

category_data={
  "name": "string",
  "description": "string"
}

product_data={
  "name": "string",
  "SKU": "string",
  "price": 0,
  "category": "string"
}


class TestMain(unittest.TestCase):
    def test_login(self):
        response=client.post("/createUser",json=data)
        assert response.status_code==200

    def test_address(self):
        response=client.post("/addAddress",json=address_data)
        assert response.status_code==200

    def test_category(self):
        response=client.post("/addCategory",json=category_data)
        assert response.status_code == 200

    def test_product(self):
        response=client.post("/addProduct",json=product_data)
        assert response.status_code == 200

    def test_order(self):
        response=client.post("/placeOrder",json=order_data)
        assert response.status_code == 200

