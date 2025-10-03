from aiogram import Dispatcher

from fluent_loader import L10N_MAPPING
from middlewares import L10nMiddleware

# init dispatcher
dp = Dispatcher()

# Apply middlewares
dp.message.outer_middleware(L10nMiddleware(l10n_mapping=L10N_MAPPING))
dp.pre_checkout_query.outer_middleware(L10nMiddleware(l10n_mapping=L10N_MAPPING))
dp.callback_query.outer_middleware(L10nMiddleware(l10n_mapping=L10N_MAPPING))
