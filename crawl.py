#!/usr/bin/evn python
# -*- coding:utf-8 -*-
#下载爬虫数据并导入数据库
import urllib2
import xlrd
import MySQLdb
import os, sys, subprocess
#reload sys
#sys.setdefaultencoding('utf8')
db = MySQLdb.connect(host="192.168.137.152", user="root", passwd="111111", db="stock_master", charset='utf8')


class Spider():
    #下载文件，返回文件绝对路径
    def __init__(self, url, filename, js_filename, table, db=db):
        self.url = url
        self .filename = filename
        self.js_filename = js_filename
        self.db = db
        self.table = table


    def py_download(self):
        '''
           Download file with python urllib2,and return file path
        '''
        headers = {
                   "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1",
                   "Referer": "http://"+self.url.split('/')[2]
                   }
        req = urllib2.Request(self.url, headers=headers)
        try:
            response = urllib2.urlopen(req, timeout=3)
            with open(self.filename, "wb") as f:
                f.write(response.read())
            print ("Download success!"+self.filename)
            #如果是zip文件，则解压
            if self.filename.split('.')[-1] == 'zip':
                os.system("/usr/bin/unzip -f %s" % self.filename)
                filename = self.filename.split('.')[0]+'.zip'
            return os.path.abspath(filename)
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print ("Download Failed:Failed to reach the server")
                print ("[Reason]:", e.reason)
            elif hasattr(e, "code"):
                print ("Error code:", e.code)
                print ("Download failed")

     #下载文件，返回文件绝对路径
    def js_download(self):
        '''
          download file with casperjs,and return file path
        '''
        js_file = os.path.join(os.getcwd(), self.js_filename)
        data_file = os.path.join(os.getcwd(), "data", self.filename)
        print data_file
        #生成爬虫数据文件
        try:
            cmd = "casperjs  %s %s --web-security=false" %(js_file, self.filename)
            subprocess.call(cmd, shell=True)
        except Exception,e:
            print(u'生成数据文件出错:',e)
            sys.exit(1)
        if self.filename.split('.')[-1] == 'zip':
            os.system("/usr/bin/unzip  %s -d %s" % (data_file, os.path.dirname(data_file)))
            data_file = data_file.replace('zip', 'xls')
        if not os.path.exists(data_file):
            print(u'数据文件不存在')
            sys.exit(1)
        else:
            if not os.path.getsize(data_file):
                print(u'数据文件为空')
                sys.exit(1)
            return data_file

    def get_excel_data(self):
        data_file = self.js_download()
        try:
            excel = xlrd.open_workbook(data_file, encoding_override="cp1252")
        except Exception, e:
            print("Open Excel File Failed:", e)
            sys.exit(1)
        else:
            sheet = excel.sheet_by_index(0)
            value_sets = []
            for r in range(1, sheet.nrows):
                value = []
                for c in range(sheet.ncols):
                    value.append(sheet.cell(r, c).value)
                value_sets.append(value)
            return value_sets, sheet.nrows

    def get_file_data(self):
        value_sets = []
        with open(self.filename, 'rb') as data:
            count = 0
            for line in data:
                value = line.decode("gb2312").encode("utf-8").split()
                value_sets.append(value)
                count += 1
        return value_sets, count


    def get_insert_sql(self):
        #获取table字段list,返回插入数据sql语句
        global db
        try:
            cursor = db.cursor()
            cursor.execute("select * from %s limit 1" % self.table)
            field_name_list = [each[0] for each in cursor.description]
            del field_name_list[0]  #去除自增id字段名
            column_list = "(" + ",".join([field for field in field_name_list]) + ")"
            values_format = "values(" + ("%s,"*len(field_name_list)).rstrip(',') + ")"
            cursor.close()
            db.close()
        except Exception, e:
            print("Error: %s" % e)
        finally:
            cursor.close()
            db.close
        insert_sql = "INSERT INTO %s" % self.table+column_list + values_format
        return insert_sql

    def save(self):
        global db
        value_sets, count = self.get_file_data()
        insert_sql = self.get_insert_sql()
        try:
            cursor = db.cursor()
            cursor.executemany(insert_sql, value_sets)
            db.commit()
            print (u"成功插入数据%d条" % count)
        except Exception, e:
            db.rollback()
            print Exception, ":", e
            print (u"插入数据失败，数据回滚")
            sys.exit(1)
        finally:
            cursor.close()
            db.close()