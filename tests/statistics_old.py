import os
import sys

import pymysql
import pandas as pd
import datetime
import json
from  sqlalchemy import create_engine

conn=create_engine('mysql+pymysql://xh:0@172.18.40.31:3306/poker2')

sql = "select game_id from player where name='x.h.v3m.1'"
df1 = pd.read_sql(sql, conn)



