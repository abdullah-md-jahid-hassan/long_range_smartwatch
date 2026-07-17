from django.contrib import admin
from django.urls import path, include
from core.views import HealthReportView

handler404 = "core.utils.exception_handler.handle_404"
handler500 = "core.utils.exception_handler.handle_500"

urlpatterns = [
    path("",       HealthReportView.as_view(), name="health"),
    path("admin/", admin.site.urls),
    path("v1/",    include(("my_django.urls_v1", "v1"))),
]
