from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class CorsMiddleWare(MiddlewareMixin):

    def process_response(self, request, response):
        if request.method == "OPTIONS":
            response["Access-Control-Allow-Methods"] = "GET,POST,DELETE,PUT"
            response["Access-Control-Allow-Headers"] = "Content-Type,AUTHORIZATION,x-token"

        try:
            response["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN")
            response["Access-Control-Allow-Credentials"] = 'true'

            response["Cache-Control"] = "no-cache"
        except Exception as e:
            logger.error(e)
        return response
