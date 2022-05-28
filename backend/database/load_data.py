from __future__ import print_function
from unicodedata import name

import sqlalchemy
import json

import googleapiclient.http
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http


def create_connection():

    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            "mssql+pytds",
            username="sqlserver",
            password="",
            database="",
            host="127.0.0.1",
            port="1433",
        ),
        echo=True,
        pool_pre_ping=True
    )
    return pool

def connect_drive():

    scopes = ['https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scopes)

    http_auth = credentials.authorize(Http())
    drive = build('drive', 'v3', http=http_auth)

    return drive

def upload_image(image_name, image_path, drive_service, parent_folder):

    file_metadata = {'name': image_name, 'parents': parent_folder}
    media = googleapiclient.http.MediaFileUpload(image_path,
                            mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    return file.get('id')

def create_folder(drive_service):
    file_metadata = {
        'name': 'waifus',
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = drive_service.files().create(body=file_metadata,
                                        fields='id').execute()

    return file.get('id')

def share_file(drive_service, file_id):

    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print (exception)
        else:
            print ("Permission Id: %s" % response.get('id'))

    batch = drive_service.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    batch.add(drive_service.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    batch.execute()



def main():

    pool = create_connection()
    pool.connect()
    drive_service = connect_drive()

    with open('./waifus.json') as f:
        data = json.loads(f.read())
        print(data[0])

        folder_id = create_folder(drive_service)
        share_file(drive_service, folder_id)
        print(folder_id)

        # images folder must be in the same directory as this script when executed

        for waifu in data:
            file_id = upload_image(waifu["name"], waifu["display_picture"], drive_service, folder_id)
            share_file(drive_service, file_id)
            url = "https://drive.google.com/file/d/" + file_id
            print(url)
            pool.execute("INSERT INTO waifus(ID,waifu_name,likes,display_picture,image_url,anime_name) VALUES(" + str(waifu["id"]) + ", '" + waifu["name"].replace("'", "´") + 
            "', " + str(waifu["likes"]) + ", '" + waifu["display_picture"] + "', '" + url + "', '" + waifu["series"]["name"].replace("'", "´") + "')")
            print("waifu processed: " + waifu["name"])

    
    pool.dispose()


if __name__ == "__main__":
    main()