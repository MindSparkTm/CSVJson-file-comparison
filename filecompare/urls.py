from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'upload/$', views.PaymentCsvSummary.as_view(), name='upload_file'),
    url(r'task-result/$', views.task_state, name='task-result'),
    url(r'upload_json/$', views.PaymentJsonSummary.as_view(), name='upload_json'),
    url(r'validation-summary/(?P<instance_id>\d+)/(?P<file_type>[\w\-]+)/$', views.get_validation_result,
        name='validation-result'),

]