import requests
from bs4 import BeautifulSoup
from timeit import default_timer
import httplib2
from hashlib import md5
from re import compile, sub
from random import shuffle

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}


def cnt_pages(URL):
    with requests.Session() as session:
        s = session.get(URL, headers=headers)
        soup = BeautifulSoup(s.text, 'html.parser')
        last_page = int(soup.find_all('a', attrs={'class': 'pg_lnk fl_l'})[-1].attrs['href'].split('=')[-1]) // 20
        return last_page


def get_pictures_on_page(URL):
    fix_link = compile(r'https://sun\d+-\d+.userapi.com')
    imgs = []
    with requests.Session() as session:
        s = session.get(URL, headers=headers)
        soup = BeautifulSoup(s.text, 'html.parser')
        pictures = soup.find_all('div', attrs={'class': 'page_post_sized_thumbs'})
        for num, pic in enumerate(pictures):
            if len(pic.contents) == 1:  # одна картинка в посте
                try:
                    temp = pic.contents[0].attrs['onclick'].split('"')[5].replace('\/', '/')
                    if 'http' not in temp:
                        continue  # это видео
                    imgs.append(sub(fix_link, 'https://pp.userapi.com', temp))
                except Exception as error:
                    print(f'{error}\n Поломались на {num} картинке, на странице {URL}.')
    return imgs


def all_parse(URL):
    pages = cnt_pages(URL)
    links = []
    start = default_timer()
    for k in range(pages):
        pictures = get_pictures_on_page(f'{URL}&offset={20 * k}')
        links.extend(pictures)
    print(f'Спарсили за {round(default_timer() - start, 2)}с.')
    save_links(links)
    shuffle(links)
    save_images(links[:500])


def update_image(URL):
    pages = cnt_pages(URL)
    all_links = []
    with open('links.txt', 'r') as file:
        for link in file:
            all_links.append(link.replace('\n', ''))
    links = []
    for k in range(pages):
        pictures = get_pictures_on_page(f'{URL}&offset={20 * k}')
        for link in pictures:
            if link in all_links:
                break
            links.append(link)
        else:
            continue
        break
    with open('links.txt', 'a', encoding='utf-8') as file:
        print('\n'.join(map(str, links)), file=file)
    print(f'Сохранили {len(links)} новых картинок')
    # save_images(links)


def save_images(links):
    start = default_timer()
    h = httplib2.Http('.cache')
    for img in links:
        response, content = h.request(img)
        out = open(f'..\\..\\front\\public\\img\\{md5(content).hexdigest()}.jpg', 'wb')
        out.write(content)
        out.close()
    print(f'Сохранили все изображения за {round(default_timer() - start, 2)}с.')


def save_links(links):
    with open('links.txt', 'w', encoding='utf-8') as file:
        print('\n'.join(map(str, links)), file=file)
    print('Сохранили список изображений')


if __name__ == '__main__':
    all_parse('https://vk.com/wall-73581821?own=1')
    # update_image('https://vk.com/wall-73581821?own=1')
