import pytest
from exceptions import (
    ProductExistsException,
    ProductNotCreatedException,
    ProductNotDeletedException,
    ProductNotFoundException,
    ProductNotUpdatedException,
    UserNotFoundException,
    UserNotSellerException,
)
from product import (
    ProductModel,
    create_new_product,
    delete_product,
    get_product,
    update_product_amountAvailable,
    update_product_cost,
)


product = {
    "productId": "1234e",
    "productName": "apple",
    "cost": 5,
    "amountAvailable": 500,
    "sellerId": "y6mwdzmtms1bgwaj",
}


# TEST PROBLEMS WITH PRODUCT MODEL


def test_empty_productId():
    temp_product = product.copy()
    temp_product["productId"] = ""
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_empty_productName():
    temp_product = product.copy()
    temp_product["productName"] = ""
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_valid_productName():
    temp_product = product.copy()
    temp_product["productName"] = "pear"
    try:
        ProductModel(**temp_product)
    except Exception as e:
        assert False, f"ProductName raised exception even though valid: \n {e}"


def test_cost_divisible_by_five():
    temp_product = product.copy()
    temp_product["cost"] = 6
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_cost_lesser_than_zero():
    temp_product = product.copy()
    temp_product["cost"] = -5
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_valid_cost():
    temp_product = product.copy()
    temp_product["cost"] = 100
    try:
        ProductModel(**temp_product)
    except Exception as e:
        assert False, f"Cost raised exception even though valid: \n {e}"


def test_amountAvailable_lesser_than_zero():
    temp_product = product.copy()
    temp_product["amountAvailable"] = -1
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_amountAvailable_equal_to_zero():
    temp_product = product.copy()
    temp_product["amountAvailable"] = 0
    try:
        ProductModel(**temp_product)
    except Exception as e:
        assert False, f"AmountAvailable equal to zero raised: \n {e}"


def test_amountAvailable_greater_than_zero():
    temp_product = product.copy()
    temp_product["amountAvailable"] = 10
    try:
        ProductModel(**temp_product)
    except Exception as e:
        assert False, f"AmountAvailable equal to zero raised: \n {e}"


def test_empty_sellerId():
    temp_product = product.copy()
    temp_product["sellerId"] = ""
    with pytest.raises(ValueError):
        ProductModel(**temp_product)


def test_sellerId_not_in_db():
    temp_product = product.copy()
    temp_product["sellerId"] = "ab"
    with pytest.raises(UserNotFoundException):
        ProductModel(**temp_product)


def test_sellerId_in_db():
    try:
        ProductModel(**product)
    except Exception as e:
        assert False, f"SellerId found but raised: \n {e}"


# TEST PROBLEMS WITH PRODUCT IN DATABASE


def test_product_is_created():
    product_obj = create_new_product(
        productName=product["productName"],
        cost=product["cost"],
        amountAvailable=product["amountAvailable"],
        sellerId=product["sellerId"],
    )
    assert product_obj.productName == product["productName"]
    assert product_obj.cost == product["cost"]
    assert product_obj.amountAvailable == product["amountAvailable"]
    assert product_obj.sellerId == product["sellerId"]


def test_product_already_exists():
    with pytest.raises((ProductExistsException, ProductNotCreatedException)):
        _ = create_new_product(
            productName=product["productName"],
            cost=product["cost"],
            amountAvailable=product["amountAvailable"],
            sellerId=product["sellerId"],
        )


def test_product_not_created_if_user_buyer():
    pass


def test_product_found():
    product_obj = get_product(productName=product["productName"])
    assert product_obj.productName == product["productName"]
    assert product_obj.cost == product["cost"]
    assert product_obj.amountAvailable == product["amountAvailable"]
    assert product_obj.sellerId == product["sellerId"]


def test_unknown_product_not_found():
    temp_product = product.copy()
    temp_product["productName"] = "appl"
    with pytest.raises(ProductNotFoundException):
        _ = get_product(productName=temp_product["productName"])


def test_product_updated():
    # Check product info before update
    product_obj = get_product(productName=product["productName"])
    assert product_obj.cost == 5
    assert product_obj.amountAvailable == 500

    # Check product info after update
    product_obj = update_product_cost(
        sellerId=product["sellerId"],
        productName=product["productName"],
        cost=50,
    )
    assert product_obj.cost == 50
    product_obj = update_product_amountAvailable(
        sellerId=product["sellerId"],
        productName=product["productName"],
        amountAvailable=2000,
    )
    assert product_obj.amountAvailable == 2000

    # Revert product info back to original amount
    product_obj = update_product_cost(
        sellerId=product["sellerId"],
        productName=product["productName"],
        cost=5,
    )
    assert product_obj.cost == 5
    product_obj = update_product_amountAvailable(
        sellerId=product["sellerId"],
        productName=product["productName"],
        amountAvailable=500,
    )
    assert product_obj.amountAvailable == 500


def test_product_not_updated_if_user_buyer():
    pass


def test_product_not_updated_if_user_another_seller():
    temp_product = product.copy()
    temp_product["sellerId"] = "ab13"
    with pytest.raises(
        (ProductNotFoundException, ProductNotUpdatedException, UserNotSellerException)
    ):
        _ = update_product_cost(
            sellerId=temp_product["sellerId"],
            productName=temp_product["productName"],
            cost=5,
        )
    with pytest.raises(
        (ProductNotFoundException, ProductNotUpdatedException, UserNotSellerException)
    ):
        _ = update_product_amountAvailable(
            sellerId=temp_product["sellerId"],
            productName=temp_product["productName"],
            amountAvailable=500,
        )


def test_product_not_deleted_if_user_buyer():
    pass


def test_product_not_deleted_if_user_another_seller():
    temp_product = product.copy()
    temp_product["sellerId"] = "ab13"
    with pytest.raises(
        (ProductNotFoundException, ProductNotDeletedException, UserNotSellerException)
    ):
        _ = delete_product(
            sellerId=temp_product["sellerId"], productName=temp_product["productName"]
        )


def test_product_deleted():
    assert (
        delete_product(sellerId=product["sellerId"], productName=product["productName"])
        == True
    )
