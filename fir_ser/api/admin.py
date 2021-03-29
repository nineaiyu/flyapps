from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(UserInfo)
admin.site.register(Apps)
admin.site.register(AppReleaseInfo)
admin.site.register(Token)
admin.site.register(VerifyName)
admin.site.register(AppStorage)
admin.site.register(AppUDID)
admin.site.register(AppIOSDeveloperInfo)
admin.site.register(APPSuperSignUsedInfo)
admin.site.register(APPToDeveloper)
admin.site.register(UDIDsyncDeveloper)
admin.site.register(Price)
admin.site.register(Order)
