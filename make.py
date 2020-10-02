import os
import argparse
import datetime
import shutil

import sqlite3

class makeTools:

    def getCurrentDirectryName(self):
        current_dir_name = os.getcwd().split(os.sep)[-1]
        return current_dir_name

    def getDateTime(self):
        dt_now = datetime.datetime.now().isoformat()
        date, time = dt_now.split('T')
        return date, time


class makeBackup(makeTools):

    def __init__(self, path):
        super(makeBackup, self).__init__()

        self.back_up_directory = path
        
    def getSourcePath(self):
        dir_and_file_name = os.listdir(path='.')
        source_path_list = [os.path.join(os.getcwd(), p) for p in dir_and_file_name]
        return dir_and_file_name

    def getDestinPath(self):
        cdn = super().getCurrentDirectryName()
        dt, tm = super().getDateTime()
        destination_path = os.path.join(self.back_up_directory, cdn, dt, tm) 
        return destination_path

    def copy(self):
        source = getSourcePath()
        destin = getDestinPath()

        for s, d in zip(source, destin):
            print("Now Copying ... SourcePath:{} => DestinPath:{}". format(s, d))
            shutil.copytree(s, d)


class makeParamDB(makeTools):

    def __init__(self, yaml_path, db_path):
        self.yaml_path = yaml_path
        self.db_path = db_path

        self.table_name = super().getCurrentDirectryName()
        self.db_dict = self.remove_str(self.read_yaml())
    
    def read_yaml(self):
        with open(self.yaml_path, mode="r") as f:
            param_dict = yaml.load(f)
        return param_dict
    
    def remove_str(self, param_dict):
        db_dict = {}
        for k in param_dict.keys():
            if not isinstance(param_dict[k], str):
                db_dict[k] = param_dict[k]
        return db_dict

    def check_table_name(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("select * from sqlite_master where type='table'")

        for tb in c.fetchall():
            if tb == self.table_name:
                return True
        
        return False

    
    def insert_values_sql(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        sql_code = 'INSERT INTO {} VALUES( {},'.format(self.table_name, super().getDateTime())
        for k in self.db_dict.key():
            sql_code += '{}, '.format(self.db_dict[k])
        sql_code += ')'

        c.execute(code)

        conn.commit()

        c.execute('SELECT * FROM {}'.format(self.table_name))

        conn.close()


    
    def create_table_sql(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        sql_code = 'CREATE TABLE {}'.format(self.table_name)
        sql_code += '(id INTEGER PRIMARY KEY AUTOINCREMENT, update, '
        
        for k in self.db_dict.key():
            sql_code += '{}, '.format(k)
        
        sql_code += ')'

        c.execute(sql_code)

        conn.commit()

        conn.close()





def main():
