import random
import string
from typing import Optional

import pandas as pd
from pydantic import BaseModel, validator

from exceptions import (
    ProductExistsException,
    ProductNotCreatedException,
    ProductNotDeletedException,
    ProductNotFoundException,
    ProductNotUpdatedException,
    PurchaseException,
    UserNotFoundException,
    UserNotSellerException,
)
from user_utils import write_to_csv


class ProductModel(BaseModel):
    productId: str
    productName: str
    cost: int
    amountAvailable: int
    sellerId: str

    @validator("productId")
    def empty_productId(cls, value):
        if value == "":
            raise ValueError("productId cannot be empty")
        return value

    @validator("productName")
    def empty_productName(cls, value):
        if value == "":
            raise ValueError("productName cannot be empty")
        return value

    @validator("cost")
    def cost_divisible_by_five(cls, value):
        if value % 5 != 0:
            raise ValueError("cost must be multiple of 5")
        return value

    @validator("cost")
    def cost_lesser_than_zero(cls, value):
        if value < 0:
            raise ValueError("cost must be greater than 0")
        return value

    @validator("amountAvailable")
    def amountAvailable_lesser_than_zero(cls, value):
        if value < 0:
            raise ValueError("amountAvailable must be greater than 0")
        return value

    @validator("sellerId")
    def empty_sellerId(cls, value):
        if value == "":
            raise ValueError("sellerId cannot be empty")
        return value

    @validator("sellerId")
    def sellerId_not_found(cls, value):
        pd_dataframe = pd.read_csv("./user_db.csv")
        if value not in list(pd_dataframe["id"]):
            raise UserNotFoundException("sellerId does not exist")
        del pd_dataframe
        return value


def create_new_product(
    productName: str, cost: int, amountAvailable: int, sellerId: str
) -> ProductModel:
    """Add product in db

    Args:
        productName (str): name of product
        cost (int): cost of single unit of product
        amountAvailable (int): available amount of product
        sellerId (str): user_id of seller to whom the product belongs

    Raises:
        ProductExistsException: raised if product already exists under this seller
        ProductNotCreatedException: raised if product is not added in db

    Returns:
        ProductModel: product
    """
    data = {
        "productId": "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(16)
        ),
        "productName": productName,
        "cost": cost,
        "amountAvailable": amountAvailable,
        "sellerId": sellerId,
    }
    pd_dataframe = pd.DataFrame(data=[data])
    try:  # check if product already exists
        product_dataframe = pd.read_csv("./product_db.csv")
        if list(
            product_dataframe[
                (product_dataframe["sellerId"] == sellerId)
                & (product_dataframe["productName"] == productName)
            ]["productName"]
        ):
            raise ProductExistsException("Product already exists")
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=None,
            mode="a",
        )
    except pd.errors.EmptyDataError:  # for first user data
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=["productId", "productName", "cost", "amountAvailable", "sellerId"],
            mode="a",
        )
    except Exception as e:
        raise ProductNotCreatedException("Product could not be added to db") from e
    return ProductModel(**data)


def get_product(
    productId: Optional[str] = None, productName: Optional[str] = None
) -> ProductModel:
    """Get product info from either productId or productName

    Args:
        productId (Optional[str], optional): product id. Defaults to None.
        productName (Optional[str], optional): product name. Defaults to None.

    Raises:
        ProductNotFoundException: raised if product does not exist

    Returns:
        ProductModel: product
    """
    try:
        pd_dataframe = pd.read_csv("./product_db.csv")
        if productId is not None:
            product_df = pd_dataframe[pd_dataframe["productId"] == productId]
        elif productName is not None:
            product_df = pd_dataframe[pd_dataframe["productName"] == productName]
        return ProductModel(
            **{
                key: value[0]
                for key, value in product_df.to_dict(orient="list").items()
            }
        )
    except IndexError as e:
        raise ProductNotFoundException("Username does not exist") from e


def update_product_cost(
    sellerId: str, productName: Optional[str], cost: int
) -> ProductModel:
    """Update product cost

    Args:
        sellerId (str): id of seller to whom the product belongs
        productName (Optional[str]): product name of which cost is to be updated
        cost (int, optional): updated cost value.

    Raises:
        UserNotSellerException: raised if user account is not SELLER account
        ProductNotFoundException: raised if product is not found
        ProductNotUpdatedException: raised if product could not be updated in db

    Returns:
        ProductModel: product
    """
    try:
        pd_dataframe = pd.read_csv("./product_db.csv")
        if sellerId not in list(pd_dataframe["sellerId"]):
            raise UserNotSellerException("User is not a seller")
        if not list(
            pd_dataframe[
                (pd_dataframe["sellerId"] == sellerId)
                & (pd_dataframe["productName"] == productName)
            ]["productName"]
        ):
            raise ProductNotFoundException("Product does not exist")
        pd_dataframe.loc[
            (pd_dataframe["sellerId"] == sellerId)
            & (pd_dataframe["productName"] == productName),
            ["cost"],
        ] = cost
        product_df = pd_dataframe[
            (pd_dataframe["sellerId"] == sellerId)
            & (pd_dataframe["productName"] == productName)
        ]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=["productId", "productName", "cost", "amountAvailable", "sellerId"],
            mode="w",
        )
        return ProductModel(
            **{
                key: value[0]
                for key, value in product_df.to_dict(orient="list").items()
            }
        )
    except Exception as e:
        raise ProductNotUpdatedException("Product cost could not be updated") from e


def update_product_amountAvailable(
    sellerId: str, productName: Optional[str], amountAvailable: int
) -> ProductModel:
    """Update amount of product available

    Args:
        sellerId (str): id of seller to whom product belongs to
        productName (Optional[str]): product name of which amountAvailable is to be updated
        amountAvailable (int, optional): updated available amount

    Raises:
        UserNotSellerException: raised if user account is not SELLER account
        ProductNotFoundException: raised if product is not found
        ProductNotUpdatedException: raised if product is not updated in db

    Returns:
        ProductModel: product
    """
    try:
        pd_dataframe = pd.read_csv("./product_db.csv")
        if sellerId not in list(pd_dataframe["sellerId"]):
            raise UserNotSellerException("User is not a seller")
        if not list(
            pd_dataframe[
                (pd_dataframe["sellerId"] == sellerId)
                & (pd_dataframe["productName"] == productName)
            ]["productName"]
        ):
            raise ProductNotFoundException("Product does not exist")
        pd_dataframe.loc[
            (pd_dataframe["sellerId"] == sellerId)
            & (pd_dataframe["productName"] == productName),
            ["amountAvailable"],
        ] = amountAvailable
        product_df = pd_dataframe[
            (pd_dataframe["sellerId"] == sellerId)
            & (pd_dataframe["productName"] == productName)
        ]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=["productId", "productName", "cost", "amountAvailable", "sellerId"],
            mode="w",
        )
        return ProductModel(
            **{
                key: value[0]
                for key, value in product_df.to_dict(orient="list").items()
            }
        )
    except Exception as e:
        raise ProductNotUpdatedException(
            "Product amountAvailable could not be updated"
        ) from e


def take_product(productId: str, no_of_products: int) -> ProductModel:
    """Take product from Vending Machine

    Args:
        productId (str): id of product to be taken
        no_of_products (int): no of products needed

    Raises:
        PurchaseException: raised if the amount requested is not available
        ProductNotUpdatedException: raised if product could not be updated in db

    Returns:
        ProductModel: product
    """
    try:
        pd_dataframe = pd.read_csv("./product_db.csv")
        if (
            list(
                pd_dataframe[pd_dataframe["productId"] == productId]["amountAvailable"]
            )[0]
            < no_of_products
        ):
            raise PurchaseException("Purchase amount not available")
        pd_dataframe.loc[
            pd_dataframe["productId"] == productId, ["amountAvailable"]
        ] -= no_of_products
        product_df = pd_dataframe[(pd_dataframe["productId"] == productId)]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=["productId", "productName", "cost", "amountAvailable", "sellerId"],
            mode="w",
        )
        return ProductModel(
            **{
                key: value[0]
                for key, value in product_df.to_dict(orient="list").items()
            }
        )
    except Exception as e:
        raise ProductNotUpdatedException(
            "Product could not be taken from Vending Machine"
        ) from e


def delete_product(sellerId: str, productName: str) -> bool:
    """Delete product from db

    Args:
        sellerId (str): id of seller to whom the product belongs
        productName (str): name of the product

    Raises:
        UserNotSellerException: raised if user account is not SELLER account
        ProductNotFoundException: raised if product is not found
        ProductNotDeletedException: raised if product could not be deleted from db

    Returns:
        bool: whether product was deleted
    """
    try:
        pd_dataframe = pd.read_csv("./product_db.csv")
        if sellerId not in list(pd_dataframe["sellerId"]):
            raise UserNotSellerException("User is not a seller")
        if not list(
            pd_dataframe[
                (pd_dataframe["sellerId"] == sellerId)
                & (pd_dataframe["productName"] == productName)
            ]["productName"]
        ):
            raise ProductNotFoundException("Product does not exist")
        pd_dataframe = pd_dataframe.drop(
            index=pd_dataframe[
                (pd_dataframe["sellerId"] == sellerId)
                & (pd_dataframe["productName"] == productName)
            ].index[0]
        )
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./product_db.csv",
            header=["productId", "productName", "cost", "amountAvailable", "sellerId"],
            mode="w",
        )
        return True
    except Exception as e:
        raise ProductNotDeletedException("Product could not be deleted") from e