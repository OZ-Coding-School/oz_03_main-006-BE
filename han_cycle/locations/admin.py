from django.contrib import admin
from .models import Location, LocationImage, L_Category, LocationCategory

# Location 모델을 관리자 페이지에 등록
admin.site.register(Location)

# LocationImage, L_Category, LocationCategory 모델도 관리자 페이지에 등록 (필요에 따라 추가)
admin.site.register(LocationImage)
admin.site.register(L_Category)
admin.site.register(LocationCategory)