# -*- coding: utf-8 -*-
"""
"""
import json
import os
import re
import requests
import shutil
from datetime import datetime

import src.cache as cache

tasks_json_filename = r"../tasks.json"


class Client:
    """
    The Client for handling periodic download. The configuration file is 
    JSON based and contains various tasks to download.
    """
    
    __tasks_filename = ""
    __tasks = None
    __startHour = 0
    __startMin = 0
    __cache = {}
    
    def __init__(self, tasks_filename = ""):
        if tasks_filename == "":
            tasks_filename = tasks_json_filename
        
        if not os.path.isfile(tasks_filename):
            raise Exception('Missing file %s' % tasks_filename)            
            
        self.__tasks_filename = tasks_filename
        with open(self.__tasks_filename, 'r') as myfile:
            data = myfile.read()
            self.__tasks = json.loads(data) 
        
        #remember start time. This is used later to test for valid interval.
        self.__startHour = datetime.now().hour
        self.__startMin = datetime.now().minute
        
        #load cache for data
        self.__cache = cache.Cache()
    
    def run(self):
        """
        Run all tasks from the tasks.json configuration file

        Returns
        -------
        None.

        """
        for task in self.__tasks['Tasks']:
            self.__download_task(task)

    def __isIntervalValid(self, interval):
        """
        Validates the interval parameter of the task and matches it against the current time.        

        Parameters
        ----------
        interval : string
            The interval at which the download should be executed. This parameter has
            the format <number><m|h> for an interval in hours or minutes. The number
            of hours must be smaller or equal to 24, the number of minutes must be
            smaller or equal to 60. Usual values include 6h, 1h, 5m, 1m.

        Returns
        -------
        bool
            True if the interval matches the current time thus allowing for the task
            to be executed.

        """
        print('  Testing Interval %s on %.2d:%.2d' % (interval, self.__startHour, self.__startMin))
        regex = re.match(r'^(\d+)([hm])$', interval)
        if regex:        
            value = int(regex.group(1))
            if value == 0: #run always
                return True
            if regex.group(2) == 'm': #run every n minutes
                if value > 60:
                    print('    invalid')
                    return False
                if self.__startMin % value == 0:
                    return True
                else:
                    print('    invalid')
                    return False
            elif regex.group(2) == 'h': #run every n hours
                if value > 24 or self.__startMin != 0:
                    print('    invalid')
                    return False
                if self.__startHour % value == 0:
                    return True
                else:
                    print('    invalid')
                    return False
                
                pass
            return True
        else:
            print('    invalid')
            return False

    def __download(self, url, filename):
        """
        Handles the actual download from the given url and writes the content 
        to the given file.

        Parameters
        ----------
        url : str
            URL to  download
        filename : str
            File to which the downloaded content should be written.

        Returns
        -------
        bool
            True if successful

        """
        r = requests.get(url)
        if not r.status_code == requests.codes.ok:
            print('Download for url %s failed! Status code: %d' % (url, r.status_code))
            return False
        
        print('  Servertime: %s' % r.headers['Date'])
        #print('  Headers: %s' % r.headers)
        
        #if data for this url has not changed we don't have to create a new file
        if self.__cache.get_data_hash_for_url(url) == self.__cache.get_data_hash(r.text):
            print('  Data has not changed.')
            return False
        else:
            self.__cache.add_url(url, r.text)
    
        filename = datetime.now().strftime(filename)
        if not os.path.isabs(filename):
            filename = os.path.abspath(os.path.dirname(os.path.realpath(self.__tasks_filename)) + '/' + filename)
            
        if not os.path.isdir(os.path.dirname(filename)):
            os.mkdirs(os.path.dirname(filename))
            
        with open(filename, 'w', encoding='utf-8') as myfile:
            print('  Writing data to %s' % filename)
            myfile.write(r.text);            
        
        return True

    def __download_task(self, task):
        """
        Parameters
        ----------
        task : JSON Dictionary
            A JSON Dictionary containing one task.

        Returns
        -------
        None.

        """
        if task['URL'] == "":
            print('URL is empty. Not downloading %s' % (task['Name']))
            return

        targetDir = task['TargetDir'] if 'TargetDir' in task else ""
        if targetDir == "":
            print('Target directory is empty. Not downloading %s' % (task['Name']))
            return        

        targetFilename = task['TargetFilename'] if 'TargetFilename' in task else ""
        if targetFilename == "":
            print('Target filename is empty. Not downloading %s' % (task['Name']))
            return        

        tempTargetDir = task['TempDir'] if 'TempDir' in task else ""
        if tempTargetDir == "":
            tempTargetDir = targetDir
        
        print('\nDownload von "%s"' % (task['Name']))
       
        if not self.__isIntervalValid(task['Interval']):
            print('  Download not neccessary')
            return
        
        if self.__download(task['URL'], os.path.join(tempTargetDir, targetFilename)):
            print('  Download successful')

        #move files from temp dir to final dir
        if targetDir != tempTargetDir:
            print('  transfering from %s to %s' % (tempTargetDir, targetDir))
            #if not os.path.isdir(targetDir):
            #    os.mkdir(targetDir)
            file_names = os.listdir(tempTargetDir)    
            for file_name in file_names:
                try:
                    print('    transfering %s' % file_name)
                    shutil.move(os.path.join(tempTargetDir, file_name), os.path.join(targetDir, file_name))
                except:
                    pass

        #test for valid interval
        if 1==0:
            self.__isIntervalValid('24h')
            self.__isIntervalValid('24m')
            self.__isIntervalValid('2m')
            self.__isIntervalValid('25h')
            self.__isIntervalValid('0h')
            self.__isIntervalValid('-0h')
            self.__isIntervalValid('19h')
            self.__isIntervalValid('3m')


if __name__ == '__main__':
    clt = Client(tasks_json_filename)
    clt.run()
  