from django.urls import path
from django.conf.urls import include

from . import views

urlpatterns = [
    path('searcher/', views.searcher, name='searcher'),
    path('uploader/', include('uploader.urls'), name='upload'),
]
