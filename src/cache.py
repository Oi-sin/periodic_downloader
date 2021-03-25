# -*- coding: utf-8 -*-
"""
"""

import json
import os
from hashlib import sha256, md5

class Cache:
    """
    This class handles some caching. It basicly saves the hash of the data for a
    given url. 
    """
    
    __cachefolder = ""
    __cacheindex_filename = ""
    __cacheindex = ""
    
    def __init__(self, cachefolder = ""):
        if cachefolder == "":
            cachefolder = os.path.join(os.path.dirname(__file__), '../__cache');
            
        self.__cachefolder = cachefolder
        self.__cacheindex_filename = os.path.join(self.__cachefolder, 'index.json')
        
        print('using cache folder %s' % self.__cachefolder)
        if not os.path.isdir(self.__cachefolder):
            print('creating cache folder %s' % self.__cachefolder)
            os.mkdirs(self.__cachefolder)
        
        self.__create_index()
        
    def __create_index(self):
        """
        """
        if os.path.isfile(self.__cacheindex_filename):
            with open(self.__cacheindex_filename, 'r', encoding='utf-8') as myfile:
                data = myfile.read()
                self.__cacheindex = json.loads(data)    
        else:
            self.__cacheindex = {}
            self.__cacheindex['entries'] = {}
            
        pass
    
    def __save_index(self):
        """        
        Write the object to file.
        """
        with open(self.__cacheindex_filename, 'w', encoding='utf-8') as myfile:
            json.dump(self.__cacheindex, myfile)
    
    def __hash(self, value):
        return md5(value.encode('utf-8')).hexdigest()

    def add_url(self, url, data):
        """
        """      
        self.__create_index()
        
        hash_url = self.__hash(url)
        hash_data = self.__hash(data)
        oldhash = self.__cacheindex['entries'][hash_url] if hash_url in self.__cacheindex['entries'] else ""
        #print(url)
        #print(hash_url)
        #print(hash_data)

        if oldhash == '':        
            self.__cacheindex['entries'][hash_url] = hash_data
        else:
            self.__cacheindex['entries'][hash_url] = hash_data
            
        self.__save_index()
    
    def clear(self):
        """
        """
        self.__cacheindex.clear()
        #self.__save_index()
        if os.path.isfile(self.__cacheindex_filename):
            os.remove(self.__cacheindex_filename)
    
    def get_data_hash_for_url(self, url):
        """
        """
        if not 'entries' in self.__cacheindex:
            return ''
        
        hash_url = self.__hash(url)
        #print('cache lookup for url %s' % url)
        return self.__cacheindex['entries'][hash_url] if hash_url in self.__cacheindex['entries'] else ""
    
    def get_data_hash(self, data):        
        if data == '':
            return ''
        else:
            return self.__hash(data)
        
    def unittests(self):
        """
        """
        if self.__cacheindex is None: 
            raise ValueError('Cache index is not assigned')
        
        #Hash for an invalid url should be empty.
        testhash = self.get_data_hash_for_url('entry does not exist')
        if testhash != "":
            raise Exception('Hash for an invalid url should be empty.')
        
        #Adding url and data should return the correct hash value
        testurl = 'http://www.test.com'
        testdata = '123456'
        self.add_url(testurl, testdata)
        
        testhash = self.get_data_hash_for_url(testurl)
        if testhash != self.get_data_hash(testdata):
            raise Exception("hash for testdata %s is %s and should be %s" % (testdata, testhash, self.get_data_hash(testdata)))
        
        #Adding url and data should return the correct hash value
        testurl2 = 'http://www.test.de'
        testdata2 = '9876543'
        self.add_url(testurl2, testdata2)
        
        testhash = self.get_data_hash_for_url(testurl2)
        if testhash != self.get_data_hash(testdata2):
            raise Exception("hash for testdata %s is %s and should be %s" % (testdata2, testhash, self.get_data_hash(testdata2)))

        #adding twice should work
        self.add_url(testurl2, testdata2)
        
        #changing data for url
        testdata3 = '165846341'
        self.add_url(testurl2, testdata3)
        testhash = self.get_data_hash_for_url(testurl2)
        if testhash != self.get_data_hash(testdata3):
            raise Exception("hash for testdata %s is %s and should be %s" % (testdata3, testhash, self.get_data_hash(testdata3)))

        #adding url directly after clear should work        
        self.clear()
        self.add_url(testurl2, testdata2)

        #clear should remove all urls
        self.clear()
        testhash = self.get_data_hash_for_url(testurl2)
        if testhash != "":
            raise Exception('Hash for url should be empty after call to clear().')

if __name__ == '__main__':
    clt = Cache()
    clt.unittests()