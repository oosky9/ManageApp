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
        self.db_dict = self.add_quotation(self.read_yaml())

        self.primary_key = super().getULIDs()
    
    def read_yaml(self):
        with open(self.yaml_path, mode="r") as f:
            param_dict = yaml.load(f)
        return param_dict
    
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

        d, t = super().getDateTime()

        sql_code = 'INSERT INTO {} VALUES(\'{}\', \'{}\', \'{}\', '.format(self.table_name, self.primary_key, d, t)
        for i, k in enumerate(self.db_dict.keys()):
            if i == len(self.db_dict.keys()) - 1:
                sql_code += '{}'.format(self.db_dict[k])
            else:
                sql_code += '{}, '.format(self.db_dict[k])
        sql_code += ')'

        c.execute(sql_code)

        conn.commit()

        c.execute('SELECT * FROM {}'.format(self.table_name))

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

    def execute(self):
        
        self.create_table_sql()
        self.insert_values_sql()


def main():

    backup_dir = "D:\\Backup\\"

    do_backup = makeBackup(backup_dir)

    do_backup.copy()

    database_path = "D:\\Database\\"
    if not os.path.isdir(database_path):
        os.makedirs(database_path)
    
    database_path = os.path.join(database_path, "research.db")

    yaml_path = "./param/hypara.yaml"
    if not os.path.isfile(yaml_path):
        print('yamlファイルを作成してください．\n')
        print('''def make_log_file(args):
    import yaml

    default_path = "./param"
    default_filename = "hypara.yaml"
    if not os.path.isdir(default_path):
        os.makedirs(default_path)

    param_dict = args.__dict__

    with open(os.path.join(default_path, default_filename), mode="w") as f:
        f.write(yaml.dump(param_dict, default_flow_style=False))
                ''')

    do_database = makeParamDB(yaml_path, database_path)

    do_database.execute()


if __name__ == "__main__":
    main()
