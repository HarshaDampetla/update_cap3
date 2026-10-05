import time
import uuid
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.repositories.database import init_db
from src.controllers import (
    auth_controller,
    admin_controller,
    stock_controller,
    watchlist_controller,
    order_controller,
    portfolio_controller,
    analytics_controller
)
from src.domain.exceptions import (
    InsufficientFundsException,
    InvalidOrderStateException,
    WatchlistUpdateException,
    WatchlistLimitExceededException,
    EmailAlreadyExistsException,
    StockAlreadyExistsException,
    StockNotFoundException,
    HardDeleteProhibitedException,
    UnauthorizedRoleModificationException,
    InvalidRoleException,
    InvalidOrderInputException,
    DomainException
)

# NFR-06: Structured logging setup
logger = logging.getLogger("marketscope")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schemas on startup
    init_db()
    yield


app = FastAPI(
    title="MarketScope API",
    description="Stock Trading & Portfolio Analytics Platform (BC-AINE-006)",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local frontend (e.g. Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["x-correlation-id"]
)


# NFR-06: Correlation ID & Structured Logging Middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    start_time = time.perf_counter()

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response.headers["x-correlation-id"] = correlation_id
    logger.info(
        f'{{"correlation_id": "{correlation_id}", "method": "{request.method}", '
        f'"path": "{request.url.path}", "status_code": {response.status_code}, '
        f'"duration_ms": {duration_ms}}}'
    )
    return response


# NFR-07: Health Check Endpoint (< 1 second response)
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "marketscope",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Global Domain Exception Handlers (Mapping domain exceptions to standard HTTP error DTOs)
@app.exception_handler(InsufficientFundsException)
async def insufficient_funds_handler(request: Request, exc: InsufficientFundsException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "InsufficientFundsException",
            "message": str(exc),
            "code": exc.code,
            "available_cash": str(exc.available_cash),
            "required_funds": str(exc.required_funds),
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(InvalidOrderStateException)
async def invalid_order_state_handler(request: Request, exc: InvalidOrderStateException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "InvalidOrderStateException",
            "message": str(exc),
            "code": exc.code,
            "current_status": exc.current_status,
            "attempted_status": exc.attempted_status,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(WatchlistUpdateException)
async def watchlist_update_handler(request: Request, exc: WatchlistUpdateException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "WatchlistUpdateException",
            "message": str(exc),
            "code": exc.code,
            "invalid_symbols": exc.invalid_symbols,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(WatchlistLimitExceededException)
async def watchlist_limit_handler(request: Request, exc: WatchlistLimitExceededException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "WatchlistLimitExceededException",
            "message": str(exc),
            "code": exc.code,
            "current_count": exc.current_count,
            "max_limit": exc.max_limit,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(EmailAlreadyExistsException)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "EmailAlreadyExistsException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(StockAlreadyExistsException)
async def stock_exists_handler(request: Request, exc: StockAlreadyExistsException):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "StockAlreadyExistsException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(StockNotFoundException)
async def stock_not_found_handler(request: Request, exc: StockNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "StockNotFoundException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(HardDeleteProhibitedException)
async def hard_delete_handler(request: Request, exc: HardDeleteProhibitedException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "HardDeleteProhibitedException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(UnauthorizedRoleModificationException)
async def unauthorized_role_handler(request: Request, exc: UnauthorizedRoleModificationException):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "UnauthorizedRoleModificationException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(InvalidRoleException)
async def invalid_role_handler(request: Request, exc: InvalidRoleException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "InvalidRoleException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


@app.exception_handler(InvalidOrderInputException)
async def invalid_order_input_handler(request: Request, exc: InvalidOrderInputException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "InvalidOrderInputException",
            "message": str(exc),
            "code": exc.code,
            "ac_id": exc.ac_id
        }
    )


# Mount Feature Routers
app.include_router(auth_controller.router)
app.include_router(admin_controller.router)
app.include_router(stock_controller.router)
app.include_router(watchlist_controller.router)
app.include_router(order_controller.router)
app.include_router(portfolio_controller.router)
app.include_router(analytics_controller.router)
