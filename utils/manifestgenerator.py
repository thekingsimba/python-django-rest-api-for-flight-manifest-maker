from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from pymongo.errors import ConfigurationError, OperationFailure, NetworkTimeout
from pymongo import MongoClient
from django.conf import settings
from .template import MANIFEST_TEMPLATE
import os

def generate_manifest_file(fight_details_object):
    
    manifests = []
    manufacturer = fight_details_object.get('manufacturer', {})
    
    for data in fight_details_object.get('data', []):
        manifest_content = MANIFEST_TEMPLATE.format(
            fight_details_id=fight_details_object.get('id', ''),
            customer= settings.CUSTOMER,
            fight_type=fight_details_object.get('fightType', ''),
            departurecity=fight_details_object.get('departurecity', ''),
            serial_number=fight_details_object.get('serialNumber', ''),
            kit_number=fight_details_object.get('kitNumber', ''),
            cargo_type=fight_details_object.get('cargo_type', ''),
            fight_category=fight_details_object.get('fightCategory', ''),
            manufacturer_code=manufacturer.get('code', ''),
            manufacturer_name=manufacturer.get('name', ''),
            cargo_prefix=manufacturer.get('cargoPrefix', ''),
            fight_prefix=manufacturer.get('fightPrefix', ''),
            pilote_code=fight_details_object.get('partCode', ''),
            logisticunit=data.get('logisticunit', ''),
            comments=fight_details_object.get('comments', ''),
            created_date=fight_details_object.get('createdDate', ''),
            created_by=fight_details_object.get('createdBy', ''),
            modified_date=fight_details_object.get('modifiedDate', ''),
            modified_by=fight_details_object.get('modifiedBy', ''),
            status=fight_details_object.get('status', ''),
            bookingid=fight_details_object.get('bookingid', ''),
            cargo=data.get('cargo', ''),
            flight_plan_key=data.get('flightPlanKey', ''),
            passenger_profile_ref=data.get('passengerProfileRef', ''),
            transport_licence_key=data.get('transportLicenceKey', ''),
            licence_expiry_date=data.get('licenceExpirtyDate', ''),
            file_name=data.get('fileName', '')
        )
        manifests.append((data.get('fileName', ''), manifest_content, data.get('cargo', '')))
    
    return manifests


def create_manifest(fight_details_id):
    try:
        # Connect to DB
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.DB_NAME]
        fight_details_collection = db[settings.COLLECTION_NAME]
    except (ConfigurationError, NetworkTimeout):
        return Response({"error": "Unable to connect to the DB server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except OperationFailure:
        return Response({"error": "Operation failed in DB."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        # Fetch the fight_details_object from the collection
        fight_details_object = fight_details_collection.find_one({"id": fight_details_id})
        if not fight_details_object:
            return Response({"error": f"fight details with ID {fight_details_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the MANIFEST(s) formatter data in an array
        manifestfiles = generate_manifest_file(fight_details_object)
    except Exception as e:
        return Response({"error": f"Failed to retrieve or process fight details data - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    count = 0

    try:
        # Write each Manifest in the manifestFiles/{fight_details_id}/{cargo} folder
        for filename, content, cargo in manifestfiles:
            directory = f'media/manifestFiles/{fight_details_id}/{cargo}'
            if not os.path.exists(directory):
                os.makedirs(directory)
            filepath = os.path.join(directory, filename)
            with open(filepath, 'w') as f:
                f.write(content.strip())
                count += 1
                print(f"Generated manifest: {filepath}")
    except OSError as e:
        return Response({"error": f"File operation failed - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred - {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        client.close()

    return Response({"message": f"{count} manifest(s) successfully generated."}, status=status.HTTP_201_CREATED)