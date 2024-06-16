from aiogram import Router
from filters import IsAdmin
from .admin_panel import router as admin_panel_router
from .number_referals import router as number_referals_router
from .subscribers import router as subscribers_router
from .sending import router as sending_router
from .control_messages import router as control_messages_router
from .automessage import router as automessage_router

router = Router()
router.message.filter(IsAdmin())
router.include_routers(
    admin_panel_router,
    number_referals_router,
    subscribers_router,
    sending_router,
    automessage_router,
    control_messages_router
)
