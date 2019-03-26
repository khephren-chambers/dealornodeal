from django.urls import path

from . import views

app_name = 'uploader'
urlpatterns = [
    path('', views.save_uploaded_file, name='uploaderfunction'),
]

'''
urlpatterns = [
    path('', views.save_uploaded_file, name='uploader'),
]
'''