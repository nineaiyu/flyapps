import logging

from api.utils.auth import ApiTokenAuthentication
from api.views.login import UserInfoView

logger = logging.getLogger(__name__)


class CliUserInfoView(UserInfoView):
    authentication_classes = [ApiTokenAuthentication, ]
