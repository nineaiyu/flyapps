from django.contrib import admin

# Register your models here.
from .models import *


admin.site.register(UserInfo)
admin.site.register(Apps)
admin.site.register(AppReleaseInfo)
admin.site.register(Token)
admin.site.register(VerifyName)
admin.site.register(AppStorage)

