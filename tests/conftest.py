import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.repositories.database import Base, get_db
from src.main import app
from src.repositories.user_repository import UserRepository
from src.repositories.stock_repository import StockRepository
from src.repositories.watchlist_repository import WatchlistRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.portfolio_repository import PortfolioRepository
from src.services.auth_service import AuthService
from src.domain.entities.user import UserRole, UserStatus


from sqlalchemy.pool import StaticPool


@pytest.fixture(scope="function")
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=eng)
    return eng


@pytest.fixture(scope="function")
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_repo(db_session):
    return UserRepository(db_session)


@pytest.fixture
def stock_repo(db_session):
    return StockRepository(db_session)


@pytest.fixture
def watchlist_repo(db_session):
    return WatchlistRepository(db_session)


@pytest.fixture
def order_repo(db_session):
    return OrderRepository(db_session)


@pytest.fixture
def portfolio_repo(db_session):
    return PortfolioRepository(db_session)


@pytest.fixture
def auth_service(user_repo, portfolio_repo):
    return AuthService(user_repo, portfolio_repo)


@pytest.fixture
def seed_admin_user(auth_service):
    user = auth_service.register("admin_test@marketscope.com", "AdminPass123!")
    auth_service.user_repo.update_role(user.id, UserRole.ADMIN.value, actor_admin_id=user.id)
    return auth_service.user_repo.get_by_id(user.id)


@pytest.fixture
def seed_customer_user(auth_service):
    return auth_service.register("trader_test@marketscope.com", "TraderPass123!")


@pytest.fixture
def admin_token(auth_service, seed_admin_user):
    login_res = auth_service.login("admin_test@marketscope.com", "AdminPass123!")
    return login_res["access_token"]


@pytest.fixture
def customer_token(auth_service, seed_customer_user):
    login_res = auth_service.login("trader_test@marketscope.com", "TraderPass123!")
    return login_res["access_token"]
