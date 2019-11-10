from flickrapi import FlickrAPI
from urllib.request import urlretrieve
from pprint import pprint
import os, time, sys
import csv
from tqdm import tqdm

# import flickr key and secret
from credentials import *

wait_time = 1

search_words = sys.argv[1:-1] if type(sys.argv[-1]) is int else sys.argv[1:]
max_pages = sys.argv[-1] if type(sys.argv[-1]) is int else 1

for search_word in search_words:
    savedir = "./" + search_word
    if not os.path.exists(savedir):
        os.makedirs(savedir)    
    pages = 1
    page = 1
    with tqdm() as pbar:
        while page < pages + 1:
            # FlickrAPI(キー、シークレット、データフォーマット{json で受け取る})
            flickr = FlickrAPI(key, secret, format='parsed-json')
            result = flickr.photos.search(
                # 検索キーワード
                text = search_word,
                # 取得するデータ件数
                per_page = 500,
                # 検索するデータの種類(ここでは、写真)
                media = 'photos',
                # データの並び順(関連順)
                sort = 'relevance',
                # UI コンテンツを表示しない
                safe_search = 1,
                license = '9,10',
                # 取得したいオプションの値(url_q->画像のアドレスが入っている情報、licence -> ライセンス情報)
                extras = 'url_z, license, path_alias',
                page = 1        
            )
            photos = result['photos']
            with open('result.log', "a") as f:
                w = csv.DictWriter(f, photos['photo'][0].keys())
                w.writerows(photos['photo'])
            pages = min(photos['pages'], max_pages)
            pbar.update(1)
            page += 1
            for photo in tqdm(photos['photo']):
                if photo['license'] != 9 and photo['license'] != 10:
                    continue
                url_q = photo['url_z']
                filepath = savedir + '/' + photo['id'] + '.jpg'
                # ファイルが重複していたらスキップする
                if os.path.exists(filepath): continue
                # データをダウンロードする
                urlretrieve(url_q, filepath)
                # 重要：サーバを逼迫しないように 1 秒待つ
                time.sleep(wait_time)




