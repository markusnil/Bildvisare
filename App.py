import camera
import time
import os
from drive_utils import get_service, list_files, upload_file, download_file
from datetime import datetime

shared_folder_id = "18l_kSviqElZrFXgI_y9WsKaFeBtFpyp-"

# Authenticate and get service
service = get_service()

# List files
files = list_files(service, folder_id=shared_folder_id)
for f in files:
    print(f"{f['name']} \t ({f['id']})")


# Download file
#download_file(service, "google-file-id", "local_copy.png")


print("Opening camera application...")
time.sleep(2)

MyCam = camera.WebcamApp()
MyCam.run()

snapshot_time = str(datetime.now().year) + "_" + str(datetime.now().month) + "_" + str(datetime.now().day) + "_" + str(datetime.now().hour) + "_" + str(datetime.now().minute)
filename = "snapshot_" + snapshot_time + ".png"

os.rename("snapshot.png", filename)

#Upload new file "snapshot" to Drive:
upload_file(service, shared_folder_id, filename)

# List files
files = list_files(service, folder_id=shared_folder_id)
for f in files:
    print(f"{f['name']} \t ({f['id']})")

