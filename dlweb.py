# -*- coding: utf-8 -*-
     
'''
Created on 2017-8-7
     
@author: chen

'''

import urllib2

def get_downloadurl(url):
    f = urllib2.urlopen(url)
    web_file = f.read()
    f.close()
    d = open('11.txt','wb')
    d.write(web_file)
    d.close()


if __name__ == '__main__':
		url_ = 'http://down.shouji.360.cn/10w.txt'
		get_downloadurl(url_)