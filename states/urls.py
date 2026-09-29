from django.urls import path
from . import views


urlpatterns = [
    path(
        '<slug:slug>/',
        views.state_detail,
        name='state_detail'
    ),
]
