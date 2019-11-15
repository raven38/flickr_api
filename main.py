from flickrapi import FlickrAPI
import urllib
from urllib.request import urlretrieve
from pprint import pprint
import os, time, sys
import csv
from tqdm import tqdm

from retry import retry
from timeout_decorator import timeout, TimeoutError

# import flickr key and secret
from credentials import *

# from https://remotestance.com/blog/1118/
from contextlib import contextmanager
@contextmanager
def fetch_url(url, max_times=10, sleep_sec=5):
    """
    HTTP通信をしてステータスコード200が返ってこなかった場合、
    一定の回数再試行をします。 一定の回数試しても駄目な場合、
    最後に開いたファイルオブジェクトを返します。
    Args:
        max_times: 最大試行回数
        sleep_sec: 接続失敗時にスリープする秒数
    例:
        with fetch_url('http://www.18th-technote.com/') as f:
            f.read()
    """
    retry_count = 0
    while True:
        f = urllib.request.urlopen(url)
        try:
            retry_count += 1
            if f.getcode() == 200 or retry_count >= max_times:
                # 200が返ってくるか、最大試行回数に到達した場合
                # ファイルオブジェクトをyieldした後にループを抜けます。
                yield f
                break
            time.sleep(sleep_sec)
        finally:
            f.close()

@retry(TimeoutError, tries=3, delay=1, backoff=2)
@timeout(5)            
def save_image(filepath, obj):
    with open(filepath, "wb") as f:
        f.write(obj.read())
    

wait_time = 1

search_words = sys.argv[1:-1] if sys.argv[-1].isdecimal() else sys.argv[1:]
max_pages = int(sys.argv[-1]) if sys.argv[-1].isdecimal() else 1

for search_word in search_words:
    savedir = "./imgs/" + search_word
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
                page = page        
            )
            photos = result['photos']
            with open('result.log', "a") as f:
                w = csv.DictWriter(f, photos['photo'][0].keys())
                w.writerows(photos['photo'])
            pages = min(photos['pages'], max_pages)
            pbar.update(1)
            page += 1
            for photo in tqdm(photos['photo']):
                if photo['license'] != "9" and photo['license'] != "10":
                    continue
                if not 'url_z' in photo:
                    continue
                url_q = photo['url_z']
                filepath = savedir + '/' + photo['id'] + '.jpg'
                # ファイルが重複していたらスキップする
                if os.path.exists(filepath): continue
                # データをダウンロードする
                with fetch_url(url_q, sleep_sec=1) as f:
                    try:
                        save_image(filepath, f)                        
                    except TimeoutError as e:
                        print (url_q, filepath)

                # urlretrieve(url_q, filepath)
                # 重要：サーバを逼迫しないように 1 秒待つ
                time.sleep(wait_time)




