# -*- coding: utf-8 -*-

import shutil
from src.periodic_downloader import Client

if __name__ == '__main__':
    clt = Client('tasks_unittest.json')
    clt.run()

    #clean up    
    shutil.rmtree('__data')
