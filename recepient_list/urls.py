from django.conf.urls import include, url
from django.contrib import admin
from recepient_list import views

urlpatterns = [
    url(r'^recepients/$', views.recepientlist, name='recepients'),
    url(r'^add-team/$', views.add_team, name='add-team'),
    url(r'^get-team-data/$', views.get_team_data, name='get-team-data'),
    url(r'^add-recepient/$', views.add_recepient, name='add-recepient'),
    url(r'^edit-recepient/(?P<rec_id>\d+)/$', views.edit_recepient, name='edit-recepient'),
    url(r'^delete-recepient/(?P<rec_id>\d+)/$', views.delete_recepient, name='edit-recepient'),
    url(r'^specific-recepient/(?P<rec_id>\d+)/$', views.specific_recepient, name='specific-recepient'),
]



