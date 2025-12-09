"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import auth, categories, transactions, users

router = APIRouter(prefix="/v1")

# Include routers
router.include_router(auth.router)
router.include_router(transactions.router)
router.include_router(categories.router)
router.include_router(users.router, prefix="/users", tags=["Users"])
