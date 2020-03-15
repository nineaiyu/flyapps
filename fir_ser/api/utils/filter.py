
from api import models
from rest_framework.filters import BaseFilterBackend

class CourseFilter(BaseFilterBackend):
    """
    课程展示 过滤器
    """

    def filter_queryset(self,request, queryset, view):
        extra = {}
        print("request.query_params",request.query_params)
        category_id = str(request.query_params.get("category_id"))

        # 如果分类ID不是数字或分类ID传输的为0
        print("category_id",category_id)
        if not category_id.isdigit() or category_id == "0":
            extra = extra
        else:
            extra.update({"course_category_id":category_id})
        print("extra",extra)
        print("queryset.filter(**extra)",queryset.filter(**extra))
        return queryset.filter(**extra)