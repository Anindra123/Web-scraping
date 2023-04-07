from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
import time
import re
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob

# Really efficient image scraper
# Prerequisite : The HTML files of all the notes form "https://www.realbanknotes.com" needs to be collected
# Scraper for those html files are written in html_parsing.py

# source: https://stackoverflow.com/a/68583332/5994461


THREAD_POOL = 16

session = requests.Session()

PoolingAdapter = HTTPAdapter(pool_maxsize=THREAD_POOL,max_retries=3,pool_block=True)


parent_link = 'https://www.realbanknotes.com'
session.mount(
    'https://',
    PoolingAdapter
)



logger = logging.getLogger('request_logger')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s',level=logging.INFO)

def get_html_files_path(parent_path,files):
    lst = {}
    for file in files:
        lst[file] = glob(os.path.join(parent_path,file,'*.html'))

    return lst





def get_sorted_html_files(list):
    sorted_list = dict(sorted(list.items(),key=lambda x:len(x[1])))
    return  sorted_list





def get_img_links(html_list,parent_path):
    img_list = []
    path_list = []
    for list in html_list:

        file_url = list.split('.')[0].split('\\')[-1]
        referrer_link = f"{parent_link}/banknote/{file_url}"
        with open(list) as f:
            content = f.read()

        soup = BeautifulSoup(content,'html.parser')
        slides = soup.findAll('div',{'class':'slide'})
        img_list = [*img_list,*[(referrer_link,f"{parent_link}{img.find('img')['src']}")
                                for img in slides]]

        path_list = [*path_list,*[os.path.join(parent_path,img.find('img')['src'].split('/')[-1])
                                for img in slides]]


    return img_list,path_list








def get_images(url,img_paths):

    referer,request = url

    if os.path.exists(img_paths):
        logger.info(f"{img_paths} already exists")
        return None,None

    logger.info(f"Requesting {url}")
    response = session.get(request
                    ,headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
                              "Referer" : referer})

    logger.info(f"{url} request completed is {response.elapsed.total_seconds()}")

    if response.status_code != 200:
        logger.error(f"Error occured when requesting {response.status_code} {response.url}")

    if 500 <= response.status_code < 600:

        logger.info("Waiting five seconds before requesting again ")
        time.sleep(5)

    return response,img_paths


def threaded_image_scraping(url_list,img_paths):
    with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
        for (resp,filename) in list(executor.map(get_images,url_list,img_paths)):
            if resp != None and resp.status_code == 200:
                with open(filename,'wb') as f:
                    f.write(resp.content)
                logger.info(f"{filename} saved sucessfully")
            else:
                continue




# img_list = get_img_links(html_list)
# threaded_image_scraping(img_list)

def create_folder(path):
    if os.path.exists(path) == False:
        os.makedirs(path)
        logger.info(f'{path} created sucessfully')
        return False
    else:
        logger.info(f'{path} already exists')
        return True


def main():


    NOTE_SAVE_PATH = 'data'
    NOTE_HTML_SAVE_PATH = os.path.join(NOTE_SAVE_PATH, 'html')
    NOTE_IMG_SAVE_PATH = os.path.join(NOTE_SAVE_PATH, 'img')
    folders = ['2-Taka' ,'5-Taka'
                          ,'10-Taka'
                          ,'20-Taka'
                          ,'50-Taka'
                          ,'100-Taka'
                          ,'200-Taka'
                          ,'500-Taka'
                          ,'1000-Taka']

    for folder in folders:
        create_folder(os.path.join(NOTE_IMG_SAVE_PATH,folder))


    lst = get_html_files_path(files=folders,parent_path=NOTE_HTML_SAVE_PATH)
    sorted_list = get_sorted_html_files(lst)
    for folders,lists in sorted_list.items():
        img_links,path_list = get_img_links(lists,parent_path=os.path.join(NOTE_IMG_SAVE_PATH,folders))
        threaded_image_scraping(img_links,path_list)


if __name__ == '__main__':
    main()


