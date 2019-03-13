# from django.conf.urls import url, include
# from rest_framework_nested import routers as nested_routers
import views
from eopen.router import SharedAPIRootRouter_v1

# from apps.classification.api.v1 import views as class_views

# router = nested_routers.SimpleRouter()
router = SharedAPIRootRouter_v1()
router.register(r'', views.sentinel1_list.as_view(), base_name='sentinel1')
router.register(r'', views.sentinel2_list.as_view(), base_name='sentinel2')
router.register(r'', views.sentinel3_list.as_view(), base_name='sentinel3')




