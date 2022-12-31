import csv
import aiofiles
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient

MUSIC_URL = 'https://music.163.com'
produce_count = 0
consume_count = 0
playlist_urls = []


async def get_playlist(url):
    global produce_count, consume_count, playlist_urls
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    # print('Start at:', url)
                    soup = BeautifulSoup(await response.text(), 'lxml')
                    body = soup.find(class_="g-wrap p-pl f-pr")
                    m_cvrlst = body.find(class_="m-cvrlst f-cb")
                    playlist = m_cvrlst.find_all("li")
                    for item in playlist:
                        information_url = MUSIC_URL + item.find(
                            class_="msk").attrs['href']
                        # 单独获取封面便于保存至本地
                        cover_url = item.find('img').attrs['src']
                        playlist_urls.append([information_url, cover_url])
                        produce_count += 1
                    nextpage = body.find(class_='zbtn znxt')
                    # print('End at: ', url)
                    print('\rget url: {}'.format(produce_count), end='')
                    # print(playlist_urls[produce_count - 1])
                    if nextpage:
                        url = MUSIC_URL + nextpage.attrs['href']
                    else:
                        break
        except:
            print("Time out at: ", url)


def get_information(infromation):
    info_1 = infromation.find(class_="cntc")

    # 歌单名
    playlist_name = info_1.find(class_="f-ff2 f-brk").text
    # 描述
    try:
        describe = info_1.find(id="album-desc-more").contents[1].strip('\n')
    except:
        describe = "NULL"
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
    share_count = content_ot.find(
        class_="u-btni u-btni-share").attrs['data-count']
    # 评论数
    comment_count = content_ot.find(id="cnt_comment_count").text
    if (comment_count == '评论'):  # 无评论时
        comment_count = '0'

    info_2 = infromation.find(class_="u-title u-title-1 f-cb")
    # 歌单内歌曲数
    playlist_track_count = info_2.find(class_="more s-fc3").text
    # 播放次数
    play_count = info_2.find(id="play-count").text

    # 歌单内歌曲路径
    play_path = "D:\\data\\Music\\{}".format(playlist_id)
    playlist_information = [
        playlist_id, playlist_name, describe, creator_id, creator_name,
        created_time, playlist_track_count, play_count, fav_count, share_count,
        comment_count, play_path
    ]
    return playlist_information


async def save(savepath):
    global produce_count, consume_count, playlist_urls
    table_path = savepath + '\\playlist_information.csv'
    with open(table_path, 'a', encoding='GB18030') as out_csv_file:
        csv_file = csv.writer(out_csv_file)
        csv_file.writerow([
            'Playlist ID', 'Playlist Name', 'Describe', 'Creator ID',
            'Creator Name', 'Created time', 'Playlist Track Count', 'Play',
            'Favorite', 'Share', 'Comment', 'Play_Path'
        ])
        print()
        while consume_count < 50:
            try:
                information_url, cover_url = playlist_urls[0]
                playlist_urls.remove([information_url, cover_url])
                async with aiohttp.ClientSession() as session_info:
                    async with session_info.get(information_url) as res_info:
                        information = BeautifulSoup(await res_info.text(), 'lxml')
                        try:
                            playlist_information = get_information(information)
                        except: print('--------')
                        csv_file.writerow(playlist_information)
                async with aiohttp.ClientSession() as session_cover:
                    async with session_cover.get(cover_url) as res_cover:
                        # print('Start read cover at: ', cover_url)
                        image = await res_cover.read()
                        image_path = savepath + '\\covers\\' + playlist_information[
                            0] + '.jpg'
                        async with aiofiles.open(image_path, 'wb') as outfile:
                            await outfile.write(image)
                        # print('End read cover at: ', cover_url)
                consume_count += 1
                print("\rsave url: {}".format(consume_count), end='')
            except:
                print('\nError:****')
                await asyncio.sleep(2)
                break


async def save_database(savepath):
    global produce_count, consume_count, playlist_urls
    text_database = []
    print('Save to DataBase Start!')
    while consume_count < 100:
        try:
            information_url, cover_url = playlist_urls[0]
            playlist_urls.remove([information_url, cover_url])
            async with aiohttp.ClientSession() as session_info:
                async with session_info.get(information_url) as res_info:
                    information = BeautifulSoup(await res_info.text(), 'lxml')
                    try:
                        playlist_information = get_information(information)
                        text_database.append({'Playlist ID': playlist_information[0],
                                              'Playlist Name': playlist_information[1],
                                              'Describe': playlist_information[2],
                                              'Creator ID': playlist_information[3],
                                              'Creator Name': playlist_information[4],
                                              'Created time': playlist_information[5],
                                              'Playlist Track Count': playlist_information[6],
                                              'Play': playlist_information[7],
                                              'Favorite': playlist_information[8],
                                              'Share': playlist_information[9],
                                              'Comment': playlist_information[10],
                                              'Play_Path': playlist_information[11]})
                    except: print('--------')
            async with aiohttp.ClientSession() as session_cover:
                async with session_cover.get(cover_url) as res_cover:
                    # print('Start read cover at: ', cover_url)
                    image = await res_cover.read()
                    image_path = savepath + '\\covers\\' + playlist_information[
                        0] + '.jpg'
                    async with aiofiles.open(image_path, 'wb') as outfile:
                        await outfile.write(image)
                    # print('End read cover at: ', cover_url)
            consume_count += 1
            print("\rsave url: {}".format(consume_count), end='')
        except:
            print('\nError:****')
            await asyncio.sleep(2)
            break
    client = MongoClient('localhost', 27017)
    db = client.CloudMusic
    collection = db.infomation
    result = collection.insert_many(text_database)
    print('\nSave End\n', result)
    client.close()


if __name__ == "__main__":
    url = 'https://music.163.com/discover/playlist/?order=hot&cat=%E8%AF%B4%E5%94%B1&limit=35&offset=1400'

    savepath = "D:\\data\\get_CloudMusic_coroutin"
    '''asyncio.run(get_playlist(url))
    asyncio.run(save(savepath))'''

    loop = asyncio.get_event_loop()
    '''tasks = [loop.create_task(get_playlist(url))]
    tasks.append(loop.create_task(save(savepath)))'''
    loop.run_until_complete(get_playlist(url))
    # loop.run_until_complete(save(savepath))
    loop.run_until_complete(save_database(savepath))
    loop.close()
    '''tasks = []
    tasks.append(asyncio.ensure_future(get_playlist(url)))
    tasks.append(asyncio.ensure_future(save(savepath)))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))'''
    print('\nFinished!')
