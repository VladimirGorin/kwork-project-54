from .start import router as start_router
from .admin import router as admin_router
from .referal_invite import router as referal_invite_router
from .get_gift import router as get_gift_router

routers = [admin_router, referal_invite_router, get_gift_router, start_router]