from rest_framework.response import Response
from rest_framework import status
import zipfile
import os
from django.conf import settings
from pymongo import MongoClient


def handle_zip_file(zip_path):
    out_dir = 'media/manifestFiles/'
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    new_files = []

    # Unzip the file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            new_files.append(file_info.filename)
            zip_ref.extract(file_info, out_dir)
    
    result = []
    
    new_dirs = {os.path.dirname(f) for f in new_files}

    for dir_name in new_dirs:
        cargo_dict = {'cargoId': os.path.basename(dir_name), 'weight': '', 'code': ''}
        cargo_path = os.path.join(out_dir, dir_name)
        for file_name in os.listdir(cargo_path):
            
            cargo_file_path = f"{cargo_path}/{file_name}"
            
            if file_name.endswith('.txt'):
                cargo_dict['weight'] = file_name
                os.remove(cargo_file_path)
                
            elif file_name.endswith('.inf'):
                cargo_dict['code'] = file_name
                os.remove(cargo_file_path)

        result.append(cargo_dict)
    
    return result


def update_flight_details_in_db(fight_details_id, cargo_data):
    
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    collection = db[settings.COLLECTION_NAME]

    fight_details = collection.find_one({"id": fight_details_id})
    if not fight_details:
        print(f"Fight details with id {fight_details_id} does not exist.")
        return f"Fight details with id {fight_details_id} does not exist."

    for cargo in fight_details["data"]:
        for cargo_dict in cargo_data:
            if cargo["cargo"] == cargo_dict["cargoId"]:
                cargo["weight"] = cargo_dict["weight"]
                cargo["code"] = cargo_dict["code"]
    
    if collection.update_one({"id": fight_details_id}, {"$set": {"data": fight_details["data"]}}):
        return True 
    else:
        return False


def process_pilotingfile(piloting_zip_name):
    zip_path = f"./media/piloting_zip_uploaded/{piloting_zip_name}"
    fight_details_id = os.path.splitext(os.path.basename(zip_path))[0]

    client = MongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    collection = db[settings.COLLECTION_NAME]

    if collection.find_one({"id": fight_details_id}):
        cargo_data = handle_zip_file(zip_path)
        if update_flight_details_in_db(fight_details_id, cargo_data):
            os.remove(zip_path)
            return Response({"message": f"File uploaded and flight details with id {fight_details_id} has been updated with piloting details."}, status=status.HTTP_201_CREATED)
    else:
        os.remove(zip_path)
        return Response({"error": f"File uploaded but deleted ! REASON: no flight details found with id {fight_details_id}."}, status=status.HTTP_400_BAD_REQUEST)
