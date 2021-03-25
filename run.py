# -*- coding: utf-8 -*-

import os
from src.periodic_downloader import Client
#import periodic_downloader

if __name__ == '__main__':
    clt = Client(os.path.join(os.path.dirname(__file__), 'tasks.json'))
    clt.run()