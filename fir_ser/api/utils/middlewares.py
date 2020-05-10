from django.utils.deprecation import MiddlewareMixin


class CorsMiddleWare(MiddlewareMixin):

    def process_response(self, request, response):
        if request.method == "OPTIONS":
            response["Access-Control-Allow-Methods"] = "GET,POST,DELETE,PUT"
            response["Access-Control-Allow-Headers"] = "Content-Type,AUTHORIZATION"

        response["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN")
        response["Access-Control-Allow-Credentials"] = 'true'

        response["Cache-Control"] = "no-cache"

        return response
