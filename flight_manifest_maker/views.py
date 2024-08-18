from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils.manifestgenerator import create_manifest
from utils.checkfile_and_save import checkfile_savezip
from django.http import FileResponse, HttpResponse, Http404
from django.conf import settings
import os
import shutil
import zipfile

@api_view(["GET"])
def get_health(request):
    return Response("Backend app is running")

@api_view(["GET"])
def trigger_generate_manifest(request, fight_details_id):
    return create_manifest(fight_details_id)

@api_view(["POST"])
def upload_outfile_file_zip(request):
    if 'file' not in request.FILES:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
    uploaded_file = request.FILES['file']
    return checkfile_savezip(uploaded_file)


@api_view(["GET"])
def get_manifest(request, fight_details_id, cargo_id, filename):
    file_path = os.path.join('media', 'simFiles', f'{fight_details_id}', f'{cargo_id}', f'{filename}.INP')
    #print(file_path)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=f'{filename}.INP')
    else:
        raise Http404("File not found")

@api_view(["GET"])
def get_files(request, fight_details_id):
        folder_path = os.path.join(settings.MEDIA_ROOT, 'simFiles', fight_details_id)
        
        if not os.path.exists(folder_path):
            raise Http404("Folder not found.")
        
        # Create a zip file
        zip_filename = f"{fight_details_id}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zip_file.write(file_path, arcname)

        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={zip_filename}'

        # Delete the zip file and the original folder after serving
        os.remove(zip_path)
        shutil.rmtree(folder_path)

        return response