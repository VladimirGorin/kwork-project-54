from handlers.admin.control_messages.message_start import router as message_start_router
from handlers.admin.control_messages.message_new_referral_other import router as message_new_referral_other_router
from handlers.admin.control_messages.message_new_referral_1_left import router as message_new_referral_1_left_router
from handlers.admin.control_messages.message_getting_promocode import router as message_getting_promocode_router
from handlers.admin.control_messages.message_after_getting_promocode import (router as
                                                                             message_after_getting_promocode_router)
from handlers.admin.control_messages.control_messages import router as control_messages_router
from handlers.admin.control_messages.message_get_gift_fail import router as message_get_gift_fail_router
from handlers.admin.control_messages.message_get_gift_success import router as message_get_gift_success_router

from aiogram import Router

router = Router()
router.include_routers(message_start_router,
                       message_new_referral_other_router,
                       message_new_referral_1_left_router,
                       message_getting_promocode_router,
                       message_after_getting_promocode_router,
                       control_messages_router,
                       message_get_gift_fail_router,
                       message_get_gift_success_router)