from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.art_list, name='art_list'),
    url(r'^art_list$', views.art_list, name='art_list'),
]
