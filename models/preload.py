from ETLpostgres import to_postgres
import os


tmp_upload_folder = "../../tmp/uploads"
files = os.listdir(tmp_upload_folder)
csv = [f for f in files if f.split(".")[-1] in ("csv", "h5")]
print("csv/h5 files :", csv)
if len(csv) == 1:
    path_file = csv[0]
    print("uploading")
    table_name = path_file.split(".")[0]
    to_postgres(tmp_upload_folder + "/" + path_file, table_name, if_exists="replace")
else:
    print("No upload, not the good number of csv/h5, there can be only one")
