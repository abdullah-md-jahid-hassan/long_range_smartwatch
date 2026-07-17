from django.urls import path
from .views import test1, test2

urlpatterns = [
    # path('1/', test1.as_view(), name='test1'),
    path('2/', test2.as_view(), name='test2'),
]