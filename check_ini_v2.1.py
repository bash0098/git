# -*- coding: UTF-8 -*-

import ConfigParser
# import urllib
import urllib2
import sys
import hashlib
import os


class CheckIni():
    def __init__(self, productname, inipath):
        self.inipath = inipath
        self.productname = productname
        self.ini = None
        self.sections= None

    def readini(self):
        self.ini = ConfigParser.ConfigParser()
        self.ini.read(self.inipath)
        self.sections = self.ini.sections()

    def checkvalidity(self):
        #read product section
        assert self.productname in self.sections, "not found section :"+self.productname+"(productname)"
        productsection = self.ini.items(self.productname)
        assert productsection[0][0] == "module", "not found modules in "+self.productname+" section : "+str(productsection)
        definedsections = set()
        tmpset = set()
        tmpset.add(self.productname)
        for module in productsection[0][1].split(","):
            if module:
                tmpset.add(module)
                assert module in self.sections,"not found section : "+ module
                modulesection = self.ini.items(module)
                if modulesection[1][0] == "files0":
                    for definedsection in modulesection[1][1].split(","):
                        if definedsection:
                            definedsections.add(definedsection)
        undefinedsection = set(self.sections)-definedsections-tmpset
        absencesection = definedsections-set(self.sections)
        return undefinedsection, absencesection

    def get_url_md5(self):
        url_md5_ls = []
        for section in self.sections:
            flag = ""
            url = ""
            md5 = ""
            url_md5_diff_ls = []
            for key, value in self.ini.items(section):
                if key == "url":
                    url = value.strip()
                    continue
                if key == "md5":
                    md5 = value.strip()
                    continue
                if key == "flag":
                    flag = value
                if "diff" in key and key!="diff_method":
                    url_diff = value.split(",")[-1].strip().strip("\"")    ###通过V5后台生成的ini中多了"的后缀
                    md5_diff = value.split(",")[1].strip()
                    url_md5_diff_ls.append([url_diff, md5_diff])
                    continue
            if flag != "1" and url:
                url_md5_ls.append([url, md5])
                url_md5_ls += url_md5_diff_ls
        return url_md5_ls


def download_file(url_):
    file_name = url_.split("/")[-1]
    try:
        f = urllib2.urlopen(url_)
        data = f.read()
        with open(file_name,"wb") as code:
            code.write(data)
        f.close()
        return True, file_name
    except urllib2.HTTPError as erro:
        return False, str(erro.code)


def get_md5(file_):
    md5file = open(file_, 'rb')
    data = md5file.read()
    md5file.close()
    return str(hashlib.md5(data).hexdigest())

    
def do_check():
    client = CheckIni(product_name, ini_path)
    client.readini()
    
    #checkstyle
    undefinedsection,absencesection = client.checkvalidity()
    if undefinedsection or absencesection:
        print "check_style fail!!!"
        print "absence_section : "+str(list(absencesection))
        print "undefined_section : "+str(list(undefinedsection))
    else:
        print "check_style pass!!!"
        
    #check_url_md5
    invalid_url_ls = []
    wrong_md5_url_ls = []
    url_md5_dict = client.get_url_md5()
    for url, md5 in url_md5_dict:
        RS_boolean,RS_str = download_file(url)
        if not RS_boolean:
            print url+" : "+RS_str
            invalid_url_ls.append((url,RS_str))
        else:
            file_md5 = ""
            file_md5 = get_md5(RS_str)
            if file_md5 != md5:
                wrong_md5_url_ls.append((url,file_md5,md5))
                print url+" : Pass    MD5 : Fail"
            else:
                print url+" : Pass    MD5 : Pass"
            os.remove(RS_str)
                
    if invalid_url_ls:
        print "/n/n/ncheck_url fail!!!"
        for tmp in invalid_url_ls:
            print tmp
    else:
        print "check_url pass!!!"
         
    if wrong_md5_url_ls:
        print "/n/n/ncheck_md5 fail!!!"
        for tmp in wrong_md5_url_ls:
            print tmp
    else:
        print "check_md5 pass!!!"
        

if __name__ == "__main__":             
    global product_name
    global ini_path
    # product_name = "360mobilesafe"
    # ini_path = "2"
    product_name = str(sys.argv[1])
    ini_path = str(sys.argv[2])
    do_check()
