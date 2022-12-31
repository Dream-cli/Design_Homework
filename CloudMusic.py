import csv
import time
import queue
import requests
from threading import Thread
from bs4 import BeautifulSoup


MUSIC_URL = 'https://music.163.com'


def get_playlist(url, q):
    while True:
        try:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            body = soup.find(class_="g-wrap p-pl f-pr")
            m_cvrlst = body.find(class_="m-cvrlst f-cb")
            playlist = m_cvrlst.find_all("li")
            for item in playlist:
                information_url = MUSIC_URL + item.find(class_="msk").attrs['href']
                # 单独获取封面便于保存至本地
                cover_url = item.find('img').attrs['src']
                information = BeautifulSoup(requests.get(information_url).text, 'lxml')
                headers = {'Connection': 'close'}
                cover = requests.get(cover_url, headers=headers, verify=False)
                q.put([information, cover])
            nextpage = body.find(class_='zbtn znxt')
            if nextpage:
                url = MUSIC_URL + nextpage.attrs['href']
            else:
                break
        except:
            print("Time out!")


def get_information(infromation):
    info_1 = infromation.find(class_="cntc")

    # 歌单名
    playlist_name = info_1.find(class_="f-ff2 f-brk").text
    # 描述
    describe = info_1.find(id="album-desc-more").contents[1].strip('\n')
    # 创建者
    creator = info_1.find(class_="s-fc7")
    # 创建者名称
    creator_name = creator.text
    # 创建者id
    creator_id = creator.attrs['href'].split('=')[-1]
    # 创建时间
    created_time = info_1.find(class_="time s-fc4").text[:10]
    # 歌单ID
    content_ot = info_1.find(id="content-operation")
    playlist_id = content_ot.attrs["data-rid"]
    # 收藏次数
    fav_count = content_ot.find(class_="u-btni u-btni-fav").attrs['data-count']
    # 分享次数
    share_count = content_ot.find(class_="u-btni u-btni-share").attrs['data-count']
    # 评论数
    comment_count = content_ot.find(id="cnt_comment_count").text
    if (comment_count == '评论'):  # 无评论时
        comment_count = '0'

    info_2 = infromation.find(class_="u-title u-title-1 f-cb")
    # 歌单内歌曲数
    playlist_track_count = info_2.find(class_="more s-fc3").text
    # 播放次数
    play_count = info_2.find(id="play-count").text

    playlist_information = [
        playlist_id, playlist_name, describe, creator_id, creator_name,
        created_time, playlist_track_count, play_count, fav_count, share_count,
        comment_count
    ]
    return playlist_information


def save(savepath, q):
    table_path = savepath + '\\playlist_information.csv'
    with open(table_path, 'a', encoding='GB18030')as out_csv_file:
        csv_file = csv.writer(out_csv_file)
        csv_file.writerow([
            'Playlist ID', 'Playlist Name', 'Describe', 'Creator ID',
            'Creator Name', 'Created time', 'Playlist Track Count', 'Play',
            'Favorite', 'Share', 'Comment'])
        while True:
            try:
                information, cover = q.get(block=True, timeout=8)
                playlist_information = get_information(information)
                csv_file.writerow(playlist_information)
                image = cover.content
                image_path = savepath + '\\covers\\' + playlist_information[0] + '.jpg'
                with open(image_path, 'wb') as outfile:
                    outfile.write(image)
            except queue.Empty:
                break


if __name__ == "__main__":
    url = 'https://music.163.com/discover/playlist/?order=hot&cat=%E8%AF%B4%E5%94%B1&limit=35&offset=0'

    savepath = "D:\\data\\get_CloudMusic"
    q = queue.LifoQueue(maxsize=100)
    producer = Thread(target=get_playlist, args=(url, q))
    customer = Thread(target=save, args=(savepath, q))
    producer.start()
    customer.start()
    producer.join()
    customer.join()
    print('Finished!')
