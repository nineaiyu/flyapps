from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(UserInfo)
admin.site.register(Apps)
admin.site.register(AppReleaseInfo)
admin.site.register(Token)
admin.site.register(VerifyName)
admin.site.register(AppStorage)
admin.site.register(Price)
admin.site.register(Order)
admin.site.register(DomainCnameInfo)
admin.site.register(UserDomainInfo)
admin.site.register(UserAdDisplayInfo)
admin.site.register(AppReportInfo)
admin.site.register(RemoteClientInfo)
