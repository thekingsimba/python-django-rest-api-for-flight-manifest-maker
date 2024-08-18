from rest_framework.response import Response
from rest_framework import status
import zipfile
import os
import io
from django.core.files.storage import default_storage
from utils.pilotinghandler import process_pilotingfile
from django.conf import settings


def checkfile_savezip(uploaded_file):
    
    if not uploaded_file.name.endswith('.zip'):
        return Response({"error": "Uploaded file is not a ZIP file"}, status=status.HTTP_400_BAD_REQUEST)
    
    if uploaded_file.content_type not in ['application/zip', 'application/x-zip-compressed']:
        return Response({"error": "Invalid content type"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            pass
    except zipfile.BadZipFile:
        return Response({"error": "Uploaded file is not a valid ZIP file"}, status=status.HTTP_400_BAD_REQUEST)
    
    file_path = os.path.join('piloting_zip_uploaded', uploaded_file.name)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    try:
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return process_pilotingfile(uploaded_file.name)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)