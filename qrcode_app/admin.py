# qrcode_app/admin.py  

from django.contrib import admin  
from .models import Table, MenuItem, Order  # 导入您的模型

# 注册模型  
admin.site.register(Table)  
admin.site.register(MenuItem)
admin.site.register(Order)

#test 1