import os

# Must be set before any app module is imported.
# These override any values in .env so the test suite never touches a real database.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pizzaflow.db")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_MODEL", "test-model")
os.environ.setdefault("MENU_FILE_PATH", "tests/fixtures/pizzas.txt")
os.environ.setdefault("BASE_FILE_PATH", "tests/fixtures/bases.txt")
os.environ.setdefault("TOPPING_FILE_PATH", "tests/fixtures/toppings.txt")
os.environ.setdefault("ADMIN_USERNAME", "test-admin")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.shared.database import Base, SessionLocal, engine, get_db
from app.contexts.auth.dependencies import get_current_admin
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import pathlib
    pathlib.Path("test_pizzaflow.db").unlink(missing_ok=True)


@pytest.fixture
def db_session() -> Session:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session: Session):
    def override_get_db():
        yield db_session

    def override_get_current_admin():
        return "test-admin"

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    yield TestClient(app, raise_server_exceptions=True)
    app.dependency_overrides.clear()
