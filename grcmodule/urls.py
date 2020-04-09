from django.conf.urls import include, url
from django.contrib import admin
from grcmodule import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^upload-forecast-data/$', views.upload_forecast_data_list, name='upload-forecast-data'),
url(r'^get_upload_forecast_data_list/$', views.get_upload_forecast_data_list, name='get_upload_forecast_data_list'),
url(r'^upload-forecast-files/$', views.upload_forecast_files_form, name='upload-forecast-files'),
url(r'^delete_forecast_files/(?P<file_id>\d+)/$', views.delete_forecast_files, name='delete_forecast_files'),
url(r'^flood-index-files/$', views.flood_index_files_list, name='flood-index-files'),
url(r'^get_flood_index_files_list/$', views.get_flood_index_files_list, name='get_flood_index_files_list'),
url(r'^upload-index-files/$', views.flood_index_files_form, name='upload-index-files'),
url(r'^delete_index_files/(?P<file_id>\d+)/$', views.delete_index_files, name='delete_index_files'),
url(r'^update-weightage-parameters/$', views.flood_index_weightage_parameters_form, name='update-weightage-parameters'),
url(r'^dashboard/$', views.dashboard, name='dashboard'),
url(r'^get_dashboard_data/$', views.get_dashboard_data, name='get_dashboard_data'),
url(r'^eap_analysis/$', views.eap_analysis, name='eap_analysis'),
url(r'^cyclone-index-files/$', views.cyclone_index_files_list, name='cyclone-index-files'),
url(r'^get_cyclone_index_files_list/$', views.get_cyclone_index_files_list, name='get_cyclone_index_files_list'),
url(r'^upload-cyclone-index-files/$', views.cyclone_index_files_form, name='upload-cyclone-index-files'),
url(r'^update-cyclone-weightage-parameters/$', views.cyclone_index_weightage_parameters_form, name='update-cyclone-weightage-parameters'),
url(r'^delete_cyclone_index_files/(?P<file_id>\d+)/$', views.delete_cyclone_index_files, name='delete_cyclone_index_files'),
url(r'^upload-cyclone-forecast-data/$', views.upload_cyclone_forecast_data_list, name='upload-cyclone-forecast-data'),
url(r'^get_upload_cyclone_forecast_data_list/$', views.get_upload_cyclone_forecast_data_list, name='get_upload_cyclone_forecast_data_list'),
url(r'^upload-cyclone-forecast-files/$', views.upload_cyclone_forecast_files_form, name='upload-cyclone-forecast-files'),
url(r'^cyclone_eap_analysis/$', views.cyclone_eap_analysis, name='cyclone_eap_analysis'),
url(r'^storm_eap_analysis/$', views.storm_eap_analysis, name='storm_eap_analysis'),
url(r'^detail-flood-index/(?P<file_id>\d+)/$', views.detail_flood_index_files, name='detail_flood_index_files'),
url(r'^flood_depth_data/$', views.flood_depth_data, name='flood_depth_data'),
url(r'^flood_impact_data/$', views.flood_impact_data, name='flood_impact_data'),
url(r'^flood_potential_data/$', views.flood_potential_data, name='flood_potential_data'),
url(r'^cyclone_wind_speed_data/$', views.cyclone_wind_speed_data, name='cyclone_wind_speed_data'),
url(r'^cyclone_impact_data/$', views.cyclone_impact_data, name='cyclone_impact_data'),
url(r'^cyclone_potential_data/$', views.cyclone_potential_data, name='cyclone_potential_data'),
url(r'^storm_surge_data/$', views.storm_surge_data, name='storm_surge_data'),
url(r'^storm_impact_data/$', views.storm_impact_data, name='storm_impact_data'),
url(r'^storm_potential_data/$', views.storm_potential_data, name='storm_potential_data'),
url(r'^detail-cyclone-index/(?P<file_id>\d+)/$', views.detail_cyclone_index_files, name='detail_cyclone_index_files'),
url(r'^flood-archive-files/$', views.flood_archive_list, name='flood-archive'),
url(r'^get_flood_archive_list/$', views.get_flood_archive_list, name='get_flood_archive_list'),
url(r'^delete_flood_archive_files/(?P<file_id>\d+)/$', views.delete_flood_archive_files, name='delete_flood_archive_files'),
url(r'^cyclone-archive-files/$', views.cyclone_archive_list, name='cyclone-archive-files'),
url(r'^get_cyclone_archive_list/$', views.get_cyclone_archive_list, name='get_cyclone_archive_list'),
url(r'^delete_cyclone_archive_files/(?P<file_id>\d+)/(?P<file_type>\d+)/$', views.delete_cyclone_archive_files, name='delete_cyclone_archive_files'),
]



