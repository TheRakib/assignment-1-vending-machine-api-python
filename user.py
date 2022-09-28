import string
from enum import Enum
import random
from typing import List, Optional, Tuple

import pandas as pd
from pydantic import BaseModel, validator
from exceptions import (
    NonAllowedDepositException,
    ProductAmountUnavailableException,
    ProductNotFoundException,
    PurchaseException,
    UserExistsException,
    UserNotBuyerException,
    UserNotCreatedException,
    UserNotDeletedException,
    UserNotFoundException,
    UserNotUpdatedException,
    ZeroDepositException,
)

from product import (
    ProductModel,
    get_product,
    take_product,
)
from user_utils import hash_password, write_to_csv


class UserEnum(Enum):
    SELLER = "seller"
    BUYER = "buyer"


class UserModel(BaseModel):
    id: str
    username: str
    password: str
    deposit: int
    role: str

    @validator("id")
    def empty_id(cls, value):
        if value == "":
            raise ValueError("id cannot be empty")
        return value

    @validator("username")
    def empty_username(cls, value):
        if value == "":
            raise ValueError("username cannot be empty")
        return value

    @validator("password")
    def empty_password(cls, value):
        if value == "":
            raise ValueError("password cannot be empty")
        return value

    @validator("deposit")
    def deposit_lesser_than_zero(cls, value):
        if value < 0:
            raise ValueError("deposit must be greater than 0")
        return value


def create_new_user(username: str, password: str, role: str) -> UserModel:
    """Create new user account

    Args:
        username (str): username of user
        password (str): password of user. password will be saved in hashed form
        role (str): user account type. user account options: BUYER, SELLER

    Raises:
        UserExistsException: raised if username already exists
        UserNotCreatedException: raised if user account does not get created

    Returns:
        UserModel: user account
    """
    data = {
        "id": "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(16)
        ),
        "username": username,
        "password": hash_password(password),
        "deposit": 0,
        "role": role,
    }
    pd_dataframe = pd.DataFrame(data=[data])
    try:  # check if user already exists
        user = get_user(username=username)
        if user.username == username:
            raise UserExistsException("Username already exists")
    except UserNotFoundException:
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=None,
            mode="a",
        )
    except pd.errors.EmptyDataError:  # for first user data
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=["id", "username", "password", "deposit", "role"],
            mode="a",
        )
    except Exception as e:
        raise UserNotCreatedException("User account could not be created") from e
    return UserModel(**data)


def get_user(username: Optional[str] = None, id: Optional[str] = None) -> UserModel:
    """Get user info from username

    Args:
        username (Optional[str]): username of user account to be retrieved. Defaults to None
        id (Optional[str]): id of user account to be retrieved. Defaults to None

    Raises:
        UserNotFoundException: raised if username does not exist

    Returns:
        UserModel: user account
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        if username is not None:
            user_df = pd_dataframe[pd_dataframe["username"] == username]
        elif id is not None:
            user_df = pd_dataframe[pd_dataframe["id"] == id]
        return UserModel(
            **{key: value[0] for key, value in user_df.to_dict(orient="list").items()}
        )
    except IndexError as e:
        raise UserNotFoundException("Username does not exist") from e


def update_password(username: str, password: Optional[str] = None) -> UserModel:
    """Update password of user

    Args:
        username (str): username of user account
        password (Optional[str], optional): new updated password of user. Defaults to None.

    Raises:
        UserNotFoundException: raised if user does not exist
        UserNotUpdatedException: raised if user account is not updated

    Returns:
        UserModel: user account
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        if password is not None:
            pd_dataframe.loc[
                pd_dataframe["username"] == username, ["password"]
            ] = hash_password(password)
        user_df = pd_dataframe[pd_dataframe["username"] == username]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=["id", "username", "password", "deposit", "role"],
            mode="w",
        )
        return UserModel(
            **{key: value[0] for key, value in user_df.to_dict(orient="list").items()}
        )
    except IndexError as e:
        raise UserNotFoundException("Username does not exist") from e
    except Exception as e:
        raise UserNotUpdatedException("Password could not be updated") from e


def deposit_amount(username: str, deposit: int = 0) -> UserModel:
    """Deposit amount to user account

    Args:
        username (str): username of user
        deposit (int, optional): deposit amount. Defaults to 0.

    Raises:
        UserNotBuyerException: raised if user account is not BUYER account
        NonAllowedDepositException: raised if deposit coins are not within {5, 10, 20, 50, 100}
        UserNotFoundException: raised if user account does not exist
        UserNotUpdatedException: raised if user account is not updated

    Returns:
        UserModel: user account
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        if (
            list(pd_dataframe[pd_dataframe["username"] == username]["role"])[0]
            != UserEnum.BUYER.value
        ):
            raise UserNotBuyerException(
                "User deposit cannot be updated. User is not a buyer"
            )
        if deposit != 0:
            if deposit in {5, 10, 20, 50, 100}:
                pd_dataframe.loc[
                    pd_dataframe["username"] == username, ["deposit"]
                ] += deposit
            else:
                raise NonAllowedDepositException(
                    f"deposit of {deposit} coin is not allowed"
                )
        user_df = pd_dataframe[pd_dataframe["username"] == username]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=["id", "username", "password", "deposit", "role"],
            mode="w",
        )
        return UserModel(
            **{key: value[0] for key, value in user_df.to_dict(orient="list").items()}
        )
    except IndexError as e:
        raise UserNotFoundException("Username does not exist") from e
    except Exception as e:
        raise UserNotUpdatedException(
            "Amount could not be deposited into User account"
        ) from e


def deduct_amount(username: str, amount: int = 0) -> UserModel:
    """Deduct amount from user deposit

    Args:
        username (str): username of user
        amount (int, optional): amount to be deducted from deposit. Defaults to 0.

    Raises:
        UserNotBuyerException: raised if user account is not BUYER account
        UserNotFoundException: raised if user is not found
        UserNotUpdatedException: raised if user account is not updated

    Returns:
        UserModel: user account
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        if (
            list(pd_dataframe[pd_dataframe["username"] == username]["role"])[0]
            != UserEnum.BUYER.value
        ):
            raise UserNotBuyerException(
                "User deposit cannot be updated. User is not a buyer"
            )
        if amount != 0:
            pd_dataframe.loc[
                pd_dataframe["username"] == username, ["deposit"]
            ] -= amount
            user_df = pd_dataframe[pd_dataframe["username"] == username]
            write_to_csv(
                pd_dataframe=pd_dataframe,
                csv_file_name="./user_db.csv",
                header=["id", "username", "password", "deposit", "role"],
                mode="w",
            )
        return UserModel(
            **{key: value[0] for key, value in user_df.to_dict(orient="list").items()}
        )
    except IndexError as e:
        raise UserNotFoundException("Username does not exist") from e
    except Exception as e:
        raise UserNotUpdatedException(
            "Amount could not be deducted from User account"
        ) from e


def reset_deposit(username: str) -> UserModel:
    """Reset user deposit to zero

    Args:
        username (str): username of user

    Raises:
        UserNotBuyerException: raised if user account is not BUYER account
        UserNotFoundException: raised if user account is not found

    Returns:
        UserModel: user account
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        if (
            pd_dataframe[pd_dataframe["username"] == username]["role"][0]
            != UserEnum.BUYER.value
        ):
            raise UserNotBuyerException(
                "User deposit cannot be updated. User is not a buyer"
            )
        pd_dataframe.loc[pd_dataframe["username"] == username, ["deposit"]] = 0
        user_df = pd_dataframe[pd_dataframe["username"] == username]
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=["id", "username", "password", "deposit", "role"],
            mode="w",
        )
        return UserModel(
            **{key: value[0] for key, value in user_df.to_dict(orient="list").items()}
        )
    except IndexError as e:
        raise UserNotFoundException("Username does not exist") from e


def buy_product(
    username: str, productId: str, no_of_products: int = 1
) -> Tuple[int, ProductModel, List[int]]:
    """Buy product

    Args:
        username (str): username of buyer
        productId (str): id of product to be bought
        no_of_products (int, optional): amount of products to be bought. Defaults to 1.

    Raises:
        UserNotFoundException: raised when user is not found
        UserNotBuyerException: raised if user account is not a BUYER account
        ZeroDepositException: raised if user has zero deposit
        ProductNotFoundException: raised if requested product is not found
        ProductAmountUnavailableException: raised if requested amount is not available
        PurchaseException: raised if there is an error in the purchase
        UserNotUpdatedException: raised if user account is not updated

    Returns:
        Tuple[int, ProductModel, List[int]]: total spent, requested product model, list of changes respectively
    """
    try:
        user_obj = get_user(username=username)
    except UserNotFoundException as e:
        raise UserNotFoundException("User does not exist") from e
    if user_obj.role == UserEnum.SELLER.value:
        raise UserNotBuyerException(
            "User cannot buy product. The account is a Seller account"
        )
    if user_obj.deposit == 0:
        raise ZeroDepositException("User cannot buy without deposit")
    try:
        product_obj = get_product(productId=productId)
    except ProductNotFoundException as e:
        raise ProductNotFoundException("Product not found") from e
    if product_obj.amountAvailable < no_of_products:
        raise ProductAmountUnavailableException(
            "Requested amount of product is not available"
        )
    if user_obj.deposit < (product_obj.cost * no_of_products):
        raise PurchaseException("User has exceeded deposit amount")
    try:
        user_obj = deduct_amount(
            username=user_obj.username, amount=product_obj.cost * no_of_products
        )
        product_obj = take_product(
            productId=product_obj.productId, no_of_products=no_of_products
        )
        change = []
        amount = user_obj.deposit
        for coin in [100, 50, 20, 10, 5]:
            if amount > 0:
                num = amount // coin
                change += [coin] * num
                amount -= coin * num
        return (
            product_obj.cost * no_of_products,  # total spent
            product_obj,  # product model
            change,  # change after purchase
        )
    except Exception as e:
        _ = deposit_amount(
            username=user_obj.username, deposit=product_obj.cost * no_of_products
        )
        raise UserNotUpdatedException(
            "Product could not be bought. Amount has been reimbursed."
        ) from e


def delete_user(username: str) -> bool:
    """Delete user account

    Args:
        username (str): username of user

    Raises:
        UserNotFoundException: raised if user account is not found
        UserNotDeletedException: raised if user account is not deleted

    Returns:
        bool: whether user account has been deleted
    """
    try:
        pd_dataframe = pd.read_csv("./user_db.csv")
        pd_dataframe = pd_dataframe.drop(
            index=pd_dataframe[pd_dataframe["username"] == username].index[0]
        )
        write_to_csv(
            pd_dataframe=pd_dataframe,
            csv_file_name="./user_db.csv",
            header=["id", "username", "password", "deposit", "role"],
            mode="w",
        )
        return True
    except IndexError as e:
        raise UserNotFoundException("Username not found") from e
    except Exception as e:
        raise UserNotDeletedException("User account could not be deleted") from e
