from api import models
from api.utils import serializer

from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.filter import CourseFilter


class CourseView(ModelViewSet):
    # authentication_classes = [ExpiringTokenAuthentication,]
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseSerializer
    filter_backends = [CourseFilter,]
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response({"code": 0, "data": serializer.data})


class CourseDetailView(ModelViewSet):
    queryset = models.CourseDetail.objects.all()
    serializer_class = serializer.CourseDetailSerializer



class CourseCategoryView(ModelViewSet):
    queryset = models.CourseCategory.objects.all()
    serializer_class = serializer.CourseCategorySerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"error_no":0,"data":serializer.data})
