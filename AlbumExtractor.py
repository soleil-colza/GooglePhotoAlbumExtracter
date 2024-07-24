import os
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# .envファイルの内容を読み込む
load_dotenv()

# 環境変数からサービスアカウントキーのファイルパスを取得
KEY_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# Google Photos APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

# 認証とAPIクライアントの作成
credentials = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
service = build('photoslibrary', 'v1', credentials=credentials)

# 特定のアルバムIDを取得
def get_album_id(album_title):
    response = service.albums().list(pageSize=50).execute()
    albums = response.get('albums', [])
    for album in albums:
        if album['title'] == album_title:
            return album['id']
    return None

# アルバム内の画像を取得
def get_all_album_photos(album_id):
    photos = []
    next_page_token = None
    while True:
        body = {'albumId': album_id}
        if next_page_token:
            body['pageToken'] = next_page_token
        response = service.mediaItems().search(body=body).execute()
        photos.extend(response.get('mediaItems', []))
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return photos

# 画像をローカルに保存
def download_photo(photo_url, file_name):
    response = requests.get(photo_url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)

# メイン処理
album_title = 'your_album_title_here'  # 対象のアルバム名をここに設定
album_id = get_album_id(album_title)

if album_id:
    photos = get_all_album_photos(album_id)
    for photo in photos:
        photo_url = f"{photo['baseUrl']}=d"  # フル解像度でダウンロード
        file_name = f"{photo['id']}.jpg"
        download_photo(photo_url, file_name)
        print(f"Downloaded {file_name}")
else:
    print(f"Album titled '{album_title}' not found.")
