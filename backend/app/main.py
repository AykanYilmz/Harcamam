import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth,
    budgets,
    categories,
    exports,
    health,
    reports,
    statements,
    subscriptions,
    transactions,
)
from app.core.config import LOCAL_HOSTS, get_settings

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, root_path=settings.root_path)
    if settings.is_production and settings.smtp_host in LOCAL_HOSTS:
        # Not fatal: everything but verification emails works, and they can be resent later.
        logger.warning("SMTP_HOST is %s: verification emails will not be sent", settings.smtp_host)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(statements.router)
    app.include_router(categories.router)
    app.include_router(transactions.router)
    app.include_router(reports.router)
    app.include_router(budgets.router)
    app.include_router(subscriptions.router)
    app.include_router(exports.router)
    return app


app = create_app()
