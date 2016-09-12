from django.conf.urls import url,include
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    url(r'^$', views.index),
  	url(r'^discover/', login_required(views.discover)),
 	url(r'^follow/$', login_required(views.follow), name='follow'),
 	url(r'^unfollow/(?P<target_id>\d+)/$', login_required(views.unfollow), name='unfollow')
]
