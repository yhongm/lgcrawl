# -*- coding: utf-8 -*-
import pandas as pd
from os import path


def parse_csv():
    dir = path.dirname('.')
    print("dir:" + path.abspath(''))

    df = pd.read_csv(path.join(dir, 'jobs_all.csv'))
    r = df.groupby('classify_name')
    v = r.money.agg(['count', 'max', 'min'])
    print(v)


if __name__ == "__main__":
    parse_csv()
