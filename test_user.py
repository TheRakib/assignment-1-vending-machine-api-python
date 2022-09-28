from random import randint
import pytest
from exceptions import (
    NonAllowedDepositException,
    ProductAmountUnavailableException,
    ProductNotFoundException,
    PurchaseException,
    UserExistsException,
    UserNotBuyerException,
    UserNotCreatedException,
    UserNotFoundException,
    UserNotUpdatedException,
    ZeroDepositException,
)
from user import (
    UserModel,
    UserEnum,
    buy_product,
    create_new_user,
    delete_user,
    deposit_amount,
    get_user,
    reset_deposit,
    update_password,
)
from user_utils import hash_password, verify_password


user1 = {
    "id": "ab12",
    "username": "Johny",
    "password": "abcde",
    "deposit": 0,
    "role": UserEnum.BUYER.value,
}

user2 = {
    "id": "uqfp2h1jh8at5pvo",
    "username": "Blade",
    "password": "abc2356",
    "deposit": 0,
    "role": UserEnum.SELLER.value,
}


def test_empty_id():
    temp_user = user1.copy()
    temp_user["id"] = ""
    with pytest.raises(ValueError):
        UserModel(**temp_user)


def test_empty_username():
    temp_user = user1.copy()
    temp_user["username"] = ""
    with pytest.raises(ValueError):
        UserModel(**temp_user)


def test_empty_password():
    temp_user = user1.copy()
    temp_user["password"] = ""
    with pytest.raises(ValueError):
        UserModel(**temp_user)


def test_deposit_lesser_than_zero():
    temp_user = user1.copy()
    temp_user["deposit"] = -10
    with pytest.raises(ValueError):
        UserModel(**temp_user)


def test_buyer_is_created():
    user_obj = create_new_user(
        username=user1["username"], password=user1["password"], role=user1["role"]
    )
    assert user_obj.username == user1["username"]
    assert user_obj.password == user1["password"]
    assert user_obj.role == user1["role"]


def test_seller_is_created():
    user_obj = create_new_user(
        username=user2["username"], password=user2["password"], role=user2["role"]
    )
    assert user_obj.username == user2["username"]
    assert user_obj.password == user2["password"]
    assert user_obj.role == user2["role"]


def test_user_found():
    user_obj = get_user(username=user1["username"])
    assert user_obj.username == user1["username"]
    assert user_obj.password == user1["password"]
    assert user_obj.role == user1["role"]


def test_user_already_exists():
    with pytest.raises((UserExistsException, UserNotCreatedException)):
        _ = create_new_user(
            username=user2["username"], password=user2["password"], role=user2["role"]
        )


def test_password_does_not_match():
    temp_user = user1.copy()
    temp_user["password"] = "abcd"
    user_obj = get_user(username=temp_user["username"])
    assert (
        verify_password(
            hashed_password=user_obj.password, normal_password=temp_user["password"]
        )
        == False
    )


def test_unknown_user_not_found():
    temp_user = user1.copy()
    temp_user["username"] = "John"
    with pytest.raises(UserNotFoundException):
        _ = get_user(username=temp_user["username"])


def test_user_password_updated():
    temp_user = user1.copy()
    temp_user["password"] = "abcd"
    user_obj = update_password(
        username=temp_user["username"], password=temp_user["password"]
    )
    assert user_obj.password == hash_password(temp_user["password"])

    user_obj = update_password(username=user1["username"], password=user1["password"])
    assert user_obj.password == hash_password(user1["password"])


def test_buyer_can_deposit():
    user_obj = deposit_amount(username=user1["username"], deposit=5)
    assert user_obj.deposit == 5
    user_obj = deposit_amount(username=user1["username"], deposit=10)
    assert user_obj.deposit == 15
    user_obj = deposit_amount(username=user1["username"], deposit=20)
    assert user_obj.deposit == 35
    user_obj = deposit_amount(username=user1["username"], deposit=5)
    assert user_obj.deposit == 40
    user_obj = deposit_amount(username=user1["username"], deposit=10)
    assert user_obj.deposit == 50


def test_buyer_cannot_deposit_non_allowed_coins():
    deposit = 5
    while deposit in {5, 10, 20, 50, 100}:
        deposit = randint(1, 100)
    with pytest.raises((NonAllowedDepositException, UserNotUpdatedException)):
        _ = deposit_amount(username=user1["username"], deposit=deposit)


def test_buyer_can_buy():
    total_spent, purchased_product, change = buy_product(
        username=user1["username"], productId="81prtrvd17363a5n", no_of_products=10
    )
    assert total_spent == 50


def test_buyer_cannot_buy_with_zero_deposit():
    with pytest.raises(ZeroDepositException):
        _ = buy_product(
            username=user1["username"], productId="81prtrvd17363a5n", no_of_products=10
        )


def test_buyer_cannot_buy_more_than_deposit():
    _ = deposit_amount(username=user1["username"], deposit=20)
    _ = deposit_amount(username=user1["username"], deposit=10)
    with pytest.raises(PurchaseException):
        _ = buy_product(
            username=user1["username"], productId="81prtrvd17363a5n", no_of_products=10
        )


def test_buyer_cannot_buy_unknown_product():
    with pytest.raises(ProductNotFoundException):
        _ = buy_product(username=user1["username"], productId="1234", no_of_products=10)


def test_buyer_cannot_buy_amount_more_than_available():
    with pytest.raises(ProductAmountUnavailableException):
        _ = buy_product(
            username=user1["username"],
            productId="81prtrvd17363a5n",
            no_of_products=1000,
        )


def test_buyer_gets_change_back():
    _ = reset_deposit(username=user1["username"])
    _ = deposit_amount(username=user1["username"], deposit=10)
    _, _, change = buy_product(
        username=user1["username"], productId="81prtrvd17363a5n", no_of_products=1
    )
    assert change == [5]


def test_buyer_gets_asked_product():
    _ = reset_deposit(username=user1["username"])
    _ = deposit_amount(username=user1["username"], deposit=50)
    _, purchased_product, _ = buy_product(
        username=user1["username"], productId="81prtrvd17363a5n", no_of_products=10
    )
    assert purchased_product.productName == "apple"


# def test_buyer_can_reset_deposit():
#     user_obj = reset_deposit(username=user1["username"])
#     assert user_obj.deposit == 0


def test_seller_cannot_deposit():
    with pytest.raises((UserNotBuyerException, UserNotUpdatedException)):
        _ = deposit_amount(username=user2["username"], deposit=5)


def test_seller_cannot_buy():
    with pytest.raises(UserNotBuyerException):
        _ = buy_product(
            username=user2["username"], productId="1234e", no_of_products=10
        )


# def test_user_deleted():
#     assert delete_user(username=user1["username"]) == True
#     assert delete_user(username=user2["username"]) == True


def test_unknown_user_not_deleted():
    with pytest.raises(UserNotFoundException):
        _ = delete_user(username="John")
