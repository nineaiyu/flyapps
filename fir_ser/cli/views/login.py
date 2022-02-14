import logging

from api.views.login import UserInfoView
from common.core.auth import ApiTokenAuthentication

logger = logging.getLogger(__name__)


class CliUserInfoView(UserInfoView):
    authentication_classes = [ApiTokenAuthentication, ]
