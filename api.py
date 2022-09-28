from datetime import timedelta
import json
import uvicorn
from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from api_utils import (
    NewProductRequest,
    ProductDelete,
    ProductUpdate,
    UserBuyProduct,
    UserDeposit,
    UserRequest,
    UserUpdatePassword,
)
from product import (
    create_new_product,
    delete_product,
    get_product,
    update_product_amountAvailable,
    update_product_cost,
)

from user import (
    buy_product,
    create_new_user,
    delete_user,
    deposit_amount,
    get_user,
    update_password,
)
from user_utils import verify_password

app = FastAPI(title="Vending Machine API", prefix="/api")
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Get username of current user. This method is for authentication purposes.

    Args:
        credentials (HTTPBasicCredentials, optional): The credentials of user. Contains username and password. Defaults to Depends(security).

    Raises:
        HTTPException: raised if username or password does not match

    Returns:
        str: username
    """
    try:
        user = get_user(username=credentials.username)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e

    if not verify_password(
        hashed_password=user.password, normal_password=credentials.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


require_auth = APIRouter(
    dependencies=[Depends(get_current_username)],
)
no_require_auth = APIRouter()


@no_require_auth.get("/", tags=["Welcome"])
async def index():
    return "Welcome to Vending Machine API"


@no_require_auth.post("/user", tags=["Create_New_User"])
async def create_user_account(request: UserRequest):
    try:
        _ = create_new_user(
            username=request.username, password=request.password, role=request.role
        )
        return Response(
            content=json.dumps(
                {"message": f"User account for {request.username} successfully created"}
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.put("/user", tags=["Update_User_password"])
async def update_user_password(
    request: UserUpdatePassword, username: str = Depends(get_current_username)
):
    try:
        _ = update_password(username=username, password=request.password)
        return Response(
            content=json.dumps({"message": "Password successfully updated"}),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.delete("/user", tags=["Remove_User_account"])
async def delete_user_account(username: str = Depends(get_current_username)):
    try:
        _ = delete_user(username=username)
        return Response(
            content=json.dumps({"message": "Account successfully deleted"}),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.post("/deposit", tags=["Deposit to your account"])
async def deposit_to_user_account(
    request: UserDeposit, username: str = Depends(get_current_username)
):
    try:
        _ = deposit_amount(username=username, deposit=request.deposit)
        return Response(
            content=json.dumps(
                {"message": f"Deposit of {request.deposit} successfully added"}
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.post("/buy", tags=["Buy products"])
async def deposit_to_user_account(
    request: UserBuyProduct, username: str = Depends(get_current_username)
):
    try:
        total_spent, product_model, change = buy_product(
            username=username,
            productId=request.productId,
            no_of_products=request.no_of_products,
        )
        return Response(
            content=json.dumps(
                {
                    "message": f"You have bought {product_model.productName} successfully added",
                    "total spent": f"Total spent: {total_spent}",
                    "product description": f"Product Description: {product_model.json()}",
                    "change": f"Change: {change}",
                }
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@no_require_auth.get("/product/{productName}", tags=["Get product info"])
async def get_product_info(productName: str):
    try:
        product_info = get_product(productName=productName)
        return Response(
            content=json.dumps(
                {
                    "message": f"Product Description: {product_info.json()}",
                }
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.post("/product", tags=["Create new product"])
async def add_product_to_db(
    request: NewProductRequest, username: str = Depends(get_current_username)
):
    try:
        user_info = get_user(username=username)
        _ = create_new_product(
            productName=request.productName,
            cost=request.cost,
            amountAvailable=request.amountAvailable,
            sellerId=user_info.id,
        )
        return Response(
            content=json.dumps(
                {
                    "message": f"Product {request.productName} created successfully",
                }
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.put("/product", tags=["Update product"])
async def update_product_in_db(
    request: ProductUpdate, username: str = Depends(get_current_username)
):
    try:
        user_info = get_user(username=username)
        if request.cost is not None:
            _ = update_product_cost(
                sellerId=user_info.id,
                productName=request.productName,
                cost=request.cost,
            )
        if request.amountAvailable is not None:
            _ = update_product_amountAvailable(
                sellerId=user_info.id,
                productName=request.productName,
                amountAvailable=request.amountAvailable,
            )
        return Response(
            content=json.dumps(
                {
                    "message": f"Product {request.productName} updated successfully",
                }
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


@require_auth.delete("/product", tags=["Delete product"])
async def delete_product_from_db(
    request: ProductDelete, username: str = Depends(get_current_username)
):
    try:
        user_info = get_user(username=username)
        _ = delete_product(sellerId=user_info.id, productName=request.productName)
        return Response(
            content=json.dumps(
                {
                    "message": f"Product {request.productName} deleted successfully",
                }
            ),
            status_code=status.HTTP_200_OK,
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
            headers={"WWW-Authenticate": "Basic"},
        ) from e


app.include_router(require_auth)
app.include_router(no_require_auth)


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
