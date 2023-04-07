import os

import requests
import logging
import time
from bs4 import BeautifulSoup

pages = ['1_page.html','2_page.html','3_page.html','4_page.html']
links = ['https://www.realbanknotes.com/country/15-Bangladesh-page-1',
         'https://www.realbanknotes.com/country/15-Bangladesh-page-2',
         'https://www.realbanknotes.com/country/15-Bangladesh-page-3',
         'https://www.realbanknotes.com/country/15-Bangladesh-page-4'
         ]

logger = logging.getLogger('request_logger')
logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s',level=logging.INFO)




def get_htmls(pages,links):

    for page,link in zip(pages,links):
        if os.path.exists(os.path.join(os.getcwd(),page)) :
            logger.info(f'{os.path.join(os.getcwd(),page)} already exists')
            continue

        try:

            logger.info(f'Requesting {link}')

            res = requests.get(link
                               , headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
                    'Accept': 'application/json'})

            res.raise_for_status()

            with open(page, 'wb') as f:
                f.write(res.content)

            logger.info(f'{page} saved sucessfully')

            logger.info('Waiting for 1 minute before requesting again')

            time.sleep(60)

        except requests.exceptions.HTTPError as err:
            logger.error(err.response,exc_info=True)


get_htmls(pages=pages,links=links)


