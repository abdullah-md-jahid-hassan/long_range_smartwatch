from django.contrib import admin
from django.urls import path, include
from core.views import HealthReportView

urlpatterns = [
    path("",       HealthReportView.as_view(), name="health"),
    path("admin/", admin.site.urls),
    path("v1/",    include(("my_django.urls_v1", "v1"))),
]
