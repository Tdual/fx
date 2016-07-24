# -*- coding: utf-8 -*-

import os

def trans_month_data(target_name):
    all_file = ""
    dir_name = "/share/rateData/"+target_name+"/"
    new_dir_name = "/share/rateData/new/"+target_name+"/"

    if not os.path.exists(new_dir_name):
        os.makedirs(new_dir_name)
    # header = "日時,始値(BID),高値(BID),安値(BID),終値(BID),高値(ASK),安値(ASK)"

    for csv in os.listdir(dir_name):
        if ".csv" in csv:
            print csv
            full_path = dir_name + csv
            with open(full_path) as f:
                f.readline()
                new_file = f.read()

                f.seek(0)
                f.readline()
                all_file += f.read()

            new_path = new_dir_name + csv
            with open(new_path,"w") as fw:
                fw.write(new_file)
    with open(new_dir_name+target_name+".csv","w") as afw:
        afw.write(all_file)


if __name__ == "__main__":
    base_path = "/share/rateData/"
    for dir_name in os.listdir(base_path):
        if "2" in dir_name:
            trans_month_data(dir_name)
