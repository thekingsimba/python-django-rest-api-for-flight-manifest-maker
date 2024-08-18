from django .urls import path
from .views import trigger_generate_manifest
from .views import upload_outfile_file_zip
from .views import get_health
from .views import get_manifest
from .views import get_files

urlpatterns = [
    path('health/',get_health ,name="get_health"),
    path('file-generator/manifest/<str:fight_details_id>/',trigger_generate_manifest, name="trigger_generate_manifest"),
    path('file-generator/outfile/upload-zip/', upload_outfile_file_zip, name='upload_outfile_file_zip'),
    path('file-generator/get-manifest/<str:fight_details_id>/<str:cargo_id>/', get_manifest, name='get_manifest'),
    path('file-generator/get-files/<str:fight_details_id>/', get_files, name='get_files'),
]

