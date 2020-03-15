from rest_framework import serializers
from api import models
from api.utils.app.analyze import bytes2human,make_download_token


# class CourseCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Course
#         fields = (
#            "id",
#            "name",
#         )
#
# class CourseSerializer(serializers.ModelSerializer):
#     level = serializers.CharField(source="get_level_display")
#     coursedetail_id=serializers.CharField(source="coursedetail.pk")
#     class Meta:
#         model = models.Course
#         fields = (
#             'id',
#             'name',
#             'course_img',
#             'brief',
#             'level',
#             "coursedetail_id"
#         )
#
#     def to_representation(self, instance):
#
#         data = super(CourseSerializer, self).to_representation(instance)
#         # 购买人数
#         # data["people_buy"] = instance.order_details.all().count()
#         # 价格套餐列表
#         price_policies = instance.price_policy.all().order_by("price").only("price")
#
#         price = getattr(price_policies.first(), "price", 0)
#
#         if price_policies and price == 0:
#             is_free = True
#             price = "免费"
#             origin_price = "原价￥{}".format(price_policies.last().price)
#         else:
#             is_free = False
#             price = "￥{}".format(price)
#             origin_price = None
#
#         # 是否免费
#         data["is_free"] = is_free
#         # 展示价格
#         data["price"] = price
#         # 原价
#         data["origin_price"] = origin_price
#
#         return data
#
#
# class CourseDetailSerializer(serializers.ModelSerializer):
#
#     name=serializers.CharField(source="course.name")
#     prices = serializers.SerializerMethodField()
#     brief = serializers.StringRelatedField(source='course.brief')
#     study_all_time = serializers.StringRelatedField(source='hours')
#     level = serializers.CharField(source='course.get_level_display')
#
#     teachers_info = serializers.SerializerMethodField()
#     is_online = serializers.SerializerMethodField()
#     recommend_coursesinfo = serializers.SerializerMethodField()
#     # learnnumber = serializers.SerializerMethodField()
#     # OftenAskedQuestion = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.CourseDetail
#         fields="__all__"
#
#     def get_prices(self, obj):
#         return PricePolicySerializer(
#             obj.course.price_policy.all(), many=True, context=self.context
#         ).data
#
#     def get_study_all_time(self, obj):
#         return "30小时"
#
#
#     def get_recommend_coursesinfo(self, obj):
#         courses = RecommendCourseSerializer(obj.recommend_courses.all(), many=True)
#         return courses.data
#
#     def get_teachers_info(self, obj):
#         teachers = TeacherSerializer(obj.teachers.all(), many=True)
#         return teachers.data
#
#     def get_is_online(self, obj):
#         if obj.course.status == 0:
#             return True
#         elif obj.course.status == 2:
#             return False
#         else:
#             return ''
#
#     # def get_learnnumber(self, obj):
#     #     return obj.course.order_details.all().count()
#
#
#     # def get_OftenAskedQuestion(self, obj):
#     #     question_queryset = models.OftenAskedQuestion.objects.filter(content_type__model='Course',
#     #                                                        object_id=obj.course.id)
#     #     serializer = OftenAskedQuestionSerializer(question_queryset, many=True)
#     #     return serializer.data
#     #
#
#
# class RecommendCourseSerializer(serializers.ModelSerializer):
#
#     course_id = serializers.CharField(source="pk")
#     course_name = serializers.CharField(source="name")
#
#     class Meta:
#         model = models.Course
#         fields = ('course_id', 'course_name',)
#
#
# class PricePolicySerializer(serializers.ModelSerializer):
#     valid_period_name = serializers.StringRelatedField(source="get_valid_period_display")
#
#     class Meta:
#         model = models.PricePolicy
#         fields = ('id', 'valid_period', 'valid_period_name', 'price',)
#
#
# class CourseChapterSerializer(serializers.ModelSerializer):
#     chapter_name = serializers.SerializerMethodField()
#     chapter_symbol = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.CourseChapter
#         fields = (
#             'id',
#             'chapter_name',
#             'chapter_symbol',
#         )
#
#     def get_chapter_name(self, instance):
#         return '第%s章·%s' % (instance.chapter, instance.name)
#
#     def get_chapter_symbol(self, instance):
#         return "chapter_%s_%s" % (self.context.get('enrolled_course_id', 1), instance.id)
#
#     def to_representation(self, instance):
#
#         data = super(CourseChapterSerializer, self).to_representation(instance)
#
#         queryset = instance.coursesections.all().order_by("order")
#         # 获取章节对应的课时数量
#         data["section_of_count"] = queryset.count()
#         data["free_trail"] = queryset.filter(free_trail=True).exists()
#         data["coursesections"] = SectionSerializer(
#             queryset, many=True, read_only=True, context=self.context
#         ).data
#
#         return data
#
#
# class OftenAskedQuestionSerializer(serializers.ModelSerializer):
#     question_tittle = serializers.SerializerMethodField()
#     question_answer = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.OftenAskedQuestion
#         fields = ('question_tittle', 'question_answer')
#
#     def get_question_tittle(self, obj):
#         return obj.question
#
#     def get_question_answer(self, obj):
#         return obj.answer
#
#
# class TeacherSerializer(serializers.ModelSerializer):
#
#     teacher_id = serializers.CharField(source="pk")
#     teacher_name = serializers.CharField(source="name")
#     teacher_brief = serializers.CharField(source="brief")
#     teacher_image = serializers.CharField(source="image")
#
#
#     class Meta:
#         model = models.Teacher
#         fields = ('teacher_id', 'teacher_name', 'title', 'signature', 'teacher_image', 'teacher_brief')
#
#

class UserInfoSerializer(serializers.ModelSerializer):
    # gender = serializers.SerializerMethodField(source="get_gender_display")

    # def get_gender(self, obj):
    #     return obj.gender

    class Meta:
        model = models.UserInfo
        # fields="__all__"
        # exclude = ["password","is_active","user_permissions","role",]
        fields=["username","uid","qq","mobile","job","email","domain_name","last_login","first_name",'head_img']
    head_img = serializers.SerializerMethodField()
    def get_head_img(self,obj):
        return "/".join([obj.domain_name, obj.head_img])


class AppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        # depth = 1
        exclude = ["user_id", "id"]

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsSerializer(obj.has_combo,context=self.context).data

    master_release = serializers.SerializerMethodField()

    def get_master_release(self, obj):
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
        if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
            master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                      release_id=self.context.get("release_id")).first()
        if master_release_obj:

            icon_url = "/".join([obj.user_id.domain_name, master_release_obj.icon_url])
            datainfo = {
                "app_version": master_release_obj.app_version,
                "icon_url": icon_url,
                "build_version": master_release_obj.build_version,
                "release_type": master_release_obj.release_type,
                "minimum_os_version": master_release_obj.minimum_os_version,
                "created_time": master_release_obj.created_time,
                "binary_size": bytes2human(master_release_obj.binary_size),
                "release_id": master_release_obj.release_id,
                "changelog": master_release_obj.changelog,
                "binary_url":master_release_obj.binary_url,
            }

            if self.context.get("download_token", None) and self.context.get("download_token") != "download_token":
                download_url = "/".join([obj.user_id.domain_name, "download", master_release_obj.release_id])
                download_url = download_url + "?token=" + self.context.get("download_token")
                datainfo["download_url"] = download_url

            return datainfo
        else:
            return {}






class AppReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppReleaseInfo
        fields = ["app_version", "icon_url", "build_version",
                  "release_type", "minimum_os_version",
                  "created_time", "binary_size", "release_id", "size", "type", "editing", "master_color", "changelog",
                  "is_master",'download_url','binary_url']
    download_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    editing = serializers.SerializerMethodField()
    master_color = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    binary_size= serializers.SerializerMethodField()
    def get_binary_size(self,obj):
        return bytes2human(obj.binary_size)

    def get_download_url(self,obj):
        download_url = "/".join([obj.app_id.user_id.domain_name, "download", obj.release_id])
        download_url = download_url + "?token=" + make_download_token(obj.release_id,300)
        return download_url

    def get_icon_url(self, obj):
        return "/".join([obj.app_id.user_id.domain_name, obj.icon_url])

    def get_master_color(self, obj):
        if obj.is_master:
            return '#0bbd87'

    def get_size(self, obj):
        return "large"

    def get_type(self, obj):
        return "primary"

    def get_editing(self, obj):
        return {"changelog":False,"binary_url":False}
