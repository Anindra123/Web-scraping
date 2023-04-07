from bs4 import BeautifulSoup
import requests
import time
import re
import os
import logging

# DISCLAMER
# NOT EFFICIENT

# TODO :
#   MAKE THE SCRAPER EFFICIENT

p = re.compile(r"-(2|5|10|20|50|100|200|500|1000)-Taka-from-(20+\d{0,20}|19+[8-9]+[8-9])")
parent_link = 'https://www.realbanknotes.com'
NOTE_SAVE_PATH = 'data'
NOTE_HTML_SAVE_PATH = os.path.join(NOTE_SAVE_PATH,'html')
NOTE_IMG_SAVE_PATH = os.path.join(NOTE_SAVE_PATH,'img')


logger = logging.getLogger('request_logger')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s',level=logging.INFO)




def create_folder(path):
    if os.path.exists(path) == False:
        os.makedirs(path)
        logger.info(f'{path} created sucessfully')
        return False
    else:
        logger.info(f'{path} already exists')
        return True


create_folder(NOTE_HTML_SAVE_PATH)
create_folder(NOTE_IMG_SAVE_PATH)

def get_links(page_list):
    links = []
    for list in page_list:
        with open(list) as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        links = [*links , *[link for link in soup.find_all('a')]]
    return links



links = get_links(['1_page.html','2_page.html','3_page.html','4_page.html'])
print(len(links))


def get_note_links(links):
    note_links = []
    for link in links:
        if link is None or link.find('img'):
            continue
        if p.search(link.get("href", "")) is not None:
            referrer = parent_link + link.get("href", "")
            note_links.append((referrer))
    return note_links

note_links = get_note_links(links)

print(len(note_links))
def save_html(link,file_save_path):
    if os.path.exists(file_save_path):
        logger.info(f'{file_save_path} already exists')
        return
    try:

        logger.info(f'Requesting {link}')

        res = requests.get(link
                           , headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
                'Accept': 'application/json'})

        res.raise_for_status()


        with open(file_save_path, 'wb') as f:
            f.write(res.content)

        logger.info(f'{file_save_path} saved sucessfully')
        logger.info('Waiting 30 sec before requesting again')
        time.sleep(30)


    except requests.exceptions.HTTPError as err:
        logger.error(err.response, exc_info=True)


def save_note_html(folder_name,note_links):
    for link in note_links:
        file_name = f"{link.split('/')[-1]}.html"
        if link.find(folder_name) > -1:
            create_folder(os.path.join(NOTE_HTML_SAVE_PATH, folder_name))
            file_save_path = os.path.join(NOTE_HTML_SAVE_PATH,folder_name,file_name)
            save_html(link,file_save_path)


def get_all_note_htmls(folder_names,notes_links):
    for folder in folder_names:
        logger.info(f'Saving all html for {folder}')
        save_note_html(folder_name=folder,note_links=notes_links)

notes_folder = ['2-Taka','5-Taka','10-Taka','20-Taka','50-Taka','100-Taka','200-Taka','500-Taka','1000-Taka']
get_all_note_htmls(notes_folder,notes_links=note_links)

