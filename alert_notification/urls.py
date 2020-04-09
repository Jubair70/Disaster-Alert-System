from django.conf.urls import url,include
from alert_notification import views

urlpatterns = [
    url(r'^create-alert-notification/$', views.create_alert_notification, name='create-alert-notification'),
    url(r'^saved-message/$', views.saved_message_list, name='saved-message'),
    url(r'^sms-queue/$', views.sms_queue_list, name='sms-queue'),
    # url(r'^send-message-table/$', views.sent_message_with_status, name='send-message-table'),
    url(r'^sms-queue/$', views.sms_queue_insert, name='sms-queue'),
    # url(r'^send-saved-message/(?P<saved_msg_id>\d+)/$', views.send_saved_message, name='send-saved-message'),
    url(r'^save-message/$', views.save_message, name='save-message'),
    url(r'^saved-message-delete/(?P<msg_id>\d+)/$', views.saved_message_delete, name='saved-message-delete'),
    url(r'^specific-message/(?P<msg_id>\d+)/$', views.specific_saved_message, name='specific-message'),
    url(r'^edit-message/(?P<msg_id>\d+)/$', views.edit_message, name='edit-message'),
    # url(r'^sent-message-delete/(?P<msg_id>\d+)/$', views.sent_message_delete, name='sent-message-delete'),

]