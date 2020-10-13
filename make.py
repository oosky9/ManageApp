import os
import argparse
import datetime
import shutil

import yaml
import sqlite3
import ulid

from tqdm import tqdm

class makeTools:

    def getCurrentDirectryName(self):
        current_dir_name = os.getcwd().split(os.sep)[-1]
        return current_dir_name

    def getDateTime(self):
        dt_now = datetime.datetime.now().isoformat()
        date, time = dt_now.split('T')
        return date, time
    
    def getULIDs(self):
        new_id = ulid.new()
        return new_id.str


class makeBackup(makeTools):

    def __init__(self, path):
        super(makeBackup, self).__init__()

        self.back_up_directory = path
        
    def getSourcePath(self):
        dir_and_file_name = os.listdir(path='.')
        source_path_list = [os.path.join(os.getcwd(), p) for p in dir_and_file_name]
        return dir_and_file_name, source_path_list

    def getDestinPath(self):
        cdn = super().getCurrentDirectryName()
        dt, tm = super().getDateTime()
        tm = tm.replace(":", "-")
        destination_path = os.path.join(self.back_up_directory, cdn, dt, tm) 
        return destination_path

    def copy(self):
        src, source = self.getSourcePath()
        dst = self.getDestinPath()

        destin = [os.path.join(dst, s) for s in src]

        print("Now Copying ...")

        for s, d in tqdm(zip(source, destin), total=len(source)):

            try:
                shutil.copytree(s, d)
            except:
                shutil.copy(s, d)



class makeParamDB(makeTools):

    def __init__(self, yaml_path, db_path):
        self.yaml_path = yaml_path
        self.db_path = db_path

        self.table_name = super().getCurrentDirectryName()

        self.primary_key = super().getULIDs()
        self.d, self.t = super().getDateTime()

        self.stat_metrics = False


    def setYamlPath(self, yaml_path):
        self.yaml_path = yaml_path
    
    def setStateMetrics(self, stat):
        self.stat_metrics = stat
    
    def read_yaml(self):
        with open(self.yaml_path, mode="r") as f:
            param_dict = yaml.load(f)
        return param_dict
    
    def change_dict_key(self, old_key, new_key, default_value=None):
        self.db_dict[new_key] = self.db_dict.pop(old_key, default_value)
    
    def add_quotation(self, param_dict):
        db_dict = {}
        for k in param_dict.keys():

            if isinstance(param_dict[k], str):
                db_dict[k] = "\'" + param_dict[k] + "\'"

            else:
                db_dict[k] = param_dict[k]

        return db_dict
    
    def insert_values_sql(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
    
        sql_column = '( id, date, time, '
        sql_values = ' VALUES(\'{}\', \'{}\', \'{}\', '.format(self.primary_key, self.d, self.t)

        for i, k in enumerate(self.db_dict.keys()):
            if i == len(self.db_dict.keys()) - 1:
                sql_column += '{}'.format(k)
                sql_values += '{}'.format(self.db_dict[k])
            else:
                sql_column += '{}, '.format(k)
                sql_values += '{}, '.format(self.db_dict[k])

        sql_column += ')'
        sql_values += ')'

        sql_code = 'INSERT INTO {}'.format(self.table_name) + sql_column + sql_values

        c.execute(sql_code)

        conn.commit()

        c.execute('SELECT * FROM {}'.format(self.table_name))

        conn.close()

    def update_values_sql(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        for k in self.db_dict.keys():
            sql = 'UPDATE {} SET {} = {} where id="{}"'.format(self.table_name, k, self.db_dict[k], self.primary_key)
            
            c.execute(sql)
        
        conn.commit()

        conn.close()


    def create_table_sql(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        sql_code = 'CREATE TABLE IF NOT EXISTS {}'.format(self.table_name)
        sql_code += '(id, date, time, '
        
        for i, k in enumerate(self.db_dict.keys()):
            if i == len(self.db_dict.keys()) - 1:
                sql_code += '{} '.format(k)
            else:
                sql_code += '{}, '.format(k)
        
        sql_code += ')'

        c.execute(sql_code)

        conn.commit()

        conn.close()

    def alter_column_sql(self):

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('PRAGMA TABLE_INFO({})'.format(self.table_name))

        column_names = [item[1] for item in c.fetchall()]

        if self.stat_metrics:
            keys = list(self.db_dict.keys())
            for k in keys:
                new_key = 'metrics_' + k
                self.change_dict_key(k, new_key)
            
            for k in self.db_dict.keys():
                if not k in column_names:
                    c.execute('ALTER TABLE {} ADD COLUMN {};'.format(self.table_name, k))
        
        else:
            if len(column_names[3:]) < len(self.db_dict.keys()): # skip (id, date, time)
                for k in self.db_dict.keys(): 
                    if not k in column_names:
                        c.execute('ALTER TABLE {} ADD COLUMN {};'.format(self.table_name, k))
            
        conn.commit()

        conn.close()


    def execute(self):

        self.db_dict = self.add_quotation(self.read_yaml())
        
        self.create_table_sql()

        self.alter_column_sql()

        if self.stat_metrics:
            self.update_values_sql()
        else:
            self.insert_values_sql()


def main():

    backup_dir = "D:\\Research\\Backup\\"

    do_backup = makeBackup(backup_dir)

    do_backup.copy()

    database_path = "D:\\Research\\Database\\"
    if not os.path.isdir(database_path):
        os.makedirs(database_path)
    
    parameter_db_path = os.path.join(database_path, "parameter.db")

    parameter_yaml_path = "./logs/parameter.yaml"
    metrics_yaml_path = "./logs/metrics.yaml"

    if not os.path.isfile(parameter_yaml_path):
        print('parameter.yamlファイルを作成してください．\n')
        print('''def make_log_file(args):
    import yaml

    default_path = "./logs"
    default_filename = "parameter.yaml"
    if not os.path.isdir(default_path):
        os.makedirs(default_path)

    param_dict = args.__dict__

    with open(os.path.join(default_path, default_filename), mode="w") as f:
        f.write(yaml.dump(param_dict, default_flow_style=False))
        ''')

    if not os.path.isfile(metrics_yaml_path):
        print("metrics.yamlがありません。")

        do_database = makeParamDB(parameter_yaml_path, parameter_db_path)

        do_database.execute()
    
    else:
        do_database = makeParamDB(parameter_yaml_path, parameter_db_path)

        do_database.execute()

        do_database.setYamlPath(metrics_yaml_path)
        do_database.setStateMetrics(True)

        do_database.execute()


if __name__ == "__main__":
    main()
