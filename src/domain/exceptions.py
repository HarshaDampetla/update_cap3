from decimal import Decimal
from typing import Optional, List


class DomainException(Exception):
    """Base domain exception."""
    code: str = "DOMAIN_ERROR"
    ac_id: Optional[str] = None


class InsufficientFundsException(DomainException):
    """AC-08: BUY order fails when quote_price * quantity exceeds available_cash."""
    def __init__(self, available_cash: Decimal, required_funds: Decimal):
        msg = f"BUY order fails: required funds {required_funds} exceeds available cash {available_cash}"
        super().__init__(msg)
        self.available_cash = available_cash
        self.required_funds = required_funds
        self.code = "INSUFFICIENT_FUNDS"
        self.ac_id = "AC-08"


class InvalidOrderStateException(DomainException):
    """AC-07: Transitioning from terminal states or invalid states raises exception."""
    def __init__(self, current_status: str, attempted_status: str, order_id: int):
        msg = f"Cannot transition order {order_id} from {current_status} to {attempted_status}."
        super().__init__(msg)
        self.current_status = current_status
        self.attempted_status = attempted_status
        self.order_id = order_id
        self.code = "INVALID_ORDER_STATE"
        self.ac_id = "AC-07"


class WatchlistUpdateException(DomainException):
    """AC-05: Atomic watchlist operations failure."""
    def __init__(self, message: str, invalid_symbols: Optional[List[str]] = None):
        super().__init__(message)
        self.invalid_symbols = invalid_symbols or []
        self.code = "WATCHLIST_UPDATE_FAILED"
        self.ac_id = "AC-05"


class WatchlistLimitExceededException(DomainException):
    """AC-04: Customer cannot hold more than 10 watchlists."""
    def __init__(self, current_count: int, max_limit: int = 10):
        super().__init__(f"Limit reached: Customer already holds {current_count}/{max_limit} watchlists.")
        self.current_count = current_count
        self.max_limit = max_limit
        self.code = "WATCHLIST_LIMIT_EXCEEDED"
        self.ac_id = "AC-04"


class StockAlreadyExistsException(DomainException):
    """AC-03: Stock symbol already exists."""
    def __init__(self, symbol: str):
        super().__init__(f"Stock with symbol '{symbol}' already exists in catalog.")
        self.symbol = symbol
        self.code = "STOCK_ALREADY_EXISTS"
        self.ac_id = "AC-03"


class StockNotFoundException(DomainException):
    """AC-03: Stock symbol not found."""
    def __init__(self, symbol: str):
        super().__init__(f"Stock with symbol '{symbol}' was not found.")
        self.symbol = symbol
        self.code = "STOCK_NOT_FOUND"
        self.ac_id = "AC-03"


class HardDeleteProhibitedException(DomainException):
    """AC-03 & NFR-02: Hard delete of stocks or trades is strictly prohibited."""
    def __init__(self, entity: str, identifier: str):
        super().__init__(f"Hard delete prohibited for {entity} '{identifier}'. Only soft-delete or append-only allowed.")
        self.entity = entity
        self.identifier = identifier
        self.code = "HARD_DELETE_PROHIBITED"
        self.ac_id = "AC-03"


class EmailAlreadyExistsException(DomainException):
    """AC-01: User registration with already existing email."""
    def __init__(self, email: str):
        super().__init__(f"Email address '{email}' is already registered.")
        self.email = email
        self.code = "EMAIL_ALREADY_EXISTS"
        self.ac_id = "AC-01"


class InvalidRoleException(DomainException):
    """AC-02: Invalid role specified."""
    def __init__(self, role: str):
        super().__init__(f"Invalid role '{role}'. Allowed roles: CUSTOMER, ADMIN, SUSPENDED.")
        self.role = role
        self.code = "INVALID_ROLE"
        self.ac_id = "AC-02"


class UnauthorizedRoleModificationException(DomainException):
    """AC-02 & NFR-04: Non-admin attempted role update."""
    def __init__(self, message: str = "Only administrators may modify user roles."):
        super().__init__(message)
        self.code = "UNAUTHORIZED_ROLE_MODIFICATION"
        self.ac_id = "AC-02"


class InvalidOrderInputException(DomainException):
    """AC-06: Invalid order input parameters."""
    def __init__(self, message: str):
        super().__init__(message)
        self.code = "INVALID_ORDER_INPUT"
        self.ac_id = "AC-06"
