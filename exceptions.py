from dataclasses import dataclass


@dataclass
class VendingMachineException(Exception):
    """
    Base Exception class for all Crawlers

    Args:
        message (str): the message to be printed
    """

    message: str = ""

    def __str__(self) -> str:
        return self.message


class UserNotCreatedException(VendingMachineException):
    """Exception raised when Vending Machine cannot create User object"""


class UserNotFoundException(VendingMachineException):
    """Exception raised when Vending Machine cannot find User"""


class UserNotUpdatedException(VendingMachineException):
    """Exception raised when Vending Machine cannot update User info"""


class UserNotDeletedException(VendingMachineException):
    """Exception raised when Vending Machine cannot delete User object"""


class UserNotBuyerException(VendingMachineException):
    """Exception raised when User is not Buyer"""


class UserNotSellerException(VendingMachineException):
    """Exception raised when User is not Seller"""


class UserPasswordMatchException(VendingMachineException):
    """Exception raised when password of User does not match"""


class UserExistsException(VendingMachineException):
    """Exception raised when similar User object exists"""


class ProductNotCreatedException(VendingMachineException):
    """Exception raised when Vending Machine cannot create Product object"""


class ProductNotFoundException(VendingMachineException):
    """Exception raised when Vending Machine cannot find Product"""


class ProductNotUpdatedException(VendingMachineException):
    """Exception raised when Vending Machine cannot update Product info"""


class ProductNotDeletedException(VendingMachineException):
    """Exception raised when Vending Machine cannot delete Product object"""


class ProductExistsException(VendingMachineException):
    """Exception raised when similar Product object already exists"""


class ProductAmountUnavailableException(VendingMachineException):
    """Exception raised when Product object has lower available amount than requested"""


class NonAllowedDepositException(VendingMachineException):
    """Exception raised when User object tries to deposit non allowed coins"""


class ZeroDepositException(VendingMachineException):
    """Exception raised when User object tries to buy without any deposit"""


class PurchaseException(VendingMachineException):
    """Exception raised when User object tries to buy more than deposit amount"""
