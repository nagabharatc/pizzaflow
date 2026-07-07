from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.shared.config import settings
from app.shared.database import Base, SessionLocal, engine, verify_connection
from app.shared.exceptions import register_exception_handlers
from app.contexts.auth.routes import router as auth_router
from app.contexts.reference.routes import router as reference_router
from app.contexts.order.routes import router as order_router
from app.contexts.checkout.routes import router as checkout_router
from app.contexts.analytics.routes import router as analytics_router
from app.contexts.ai_advisor.routes import router as ai_advisor_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    verify_connection()
    Base.metadata.create_all(bind=engine)
    _seed_reference_data()
    yield
    engine.dispose()


_BACKEND_DIR = Path(__file__).resolve().parent.parent


def _seed_reference_data() -> None:
    from app.contexts.reference.repositories.base_repository import BaseRepository
    from app.contexts.reference.repositories.menu_repository import MenuRepository
    from app.contexts.reference.repositories.topping_repository import ToppingRepository
    from app.contexts.reference.service import MenuLoader

    with SessionLocal() as db:
        loader = MenuLoader(MenuRepository(db), BaseRepository(db), ToppingRepository(db))
        loader.seed_bases_from_file(str(_BACKEND_DIR / settings.base_file_path))
        loader.seed_toppings_from_file(str(_BACKEND_DIR / settings.topping_file_path))
        loader.seed_pizzas_from_file(str(_BACKEND_DIR / settings.menu_file_path))


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(reference_router, prefix="/menu", tags=["Menu"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(checkout_router, prefix="/checkout", tags=["Checkout"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(ai_advisor_router, prefix="/ai", tags=["AI Advisor"])


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"service": settings.app_name, "status": "healthy"}
