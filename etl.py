from collections import Counter
from numpy import dot
from numpy.linalg import norm
import json

import sqlalchemy
from sqlalchemy import create_engine
import re, time, pymysql.cursors, pymysql
import random
import os
from dotenv import load_dotenv
load_dotenv()

Host = os.getenv("Host")
User = os.getenv("User")
Password = os.getenv("Password")
Path = os.getenv("Path")

engine = create_engine(
    'mysql+pymysql://'+User+':'+Password+'@localhost/JHT',
    echo = True)
connection = engine.raw_connection()
cursor = connection.cursor()

test = 100

# skill_score table
def skill_score():
    all = list()
    kw = list()
    infos = list()
    # cursor.execute("select id,position,company from Jobs limit %s",test) 
    cursor.execute("select job_id,position,company from Joball") 
    info = list(cursor.fetchall())
    # print(info)
    for i in info:
        i = list(i)
        infos.append(i)
    # print(infos) # [[1, 'Data Engineer', 'American Express'], [2, 'Data Engineer', 'Apple'], [3, 'Data Engineer', 'HqO']]

    # kw
    # cursor.execute("select description from Jobs limit %s",test) 
    cursor.execute("select description from Jobs") 
    jds = cursor.fetchall()

    for jd in jds: 
        jd = jd[0]
        skillset = ['SQL','Python','Java','Spark','AWS','ETL']  
        count_skill = [jd.count(x) for x in set(skillset)]
        # print(count_skill) #
        dicts = dict((x,jd.count(x)) for x in set(skillset))
        # print(dicts)
        kw.append(count_skill)
    # print(kw) #[[1, 1, 4, 1, 0, 1], [1, 0, 2, 1, 0, 0], [0, 2, 1, 0, 0, 1]]

    for i in range(len(infos)):
        com = infos[i]+kw[i]
        all.append(com)

    print(len(all))
    # print(all)
    return all

def save_match(data): #INSERT INTO skill_match (`job_id`,`position`,`company`,`SQL`,`Python`,`Java`,`Spark`,`AWS`,`ETL`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    sql = "INSERT INTO skill_score (`job_id`,`position`,`company`,`SQL`,`Python`,`Java`,`Spark`,`AWS`,`ETL`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    back = cursor.executemany(sql, data)  
    connection.commit()
    print('Items save to db: ',back)

# save successfully
# save_match(skill_score())

def job_description():
    infos = list()
    # cursor.execute("select id,position,company from Jobs limit %s",test) 
    cursor.execute("select job_id,position,company from Joball") 
    info = list(cursor.fetchall())
    # print(info)
    for i in info:
        i = list(i)
        infos.append(i)
    # print(infos)    

    # brief
    all = list()
    briefs = list()
    years = list()
    # cursor.execute("select description from Jobs limit %s",test) 
    cursor.execute("select description from Jobs") 
    jds = cursor.fetchall()
    for jd in jds:
        brief = re.findall(
            r'years.*|experience in.*|experience with.*|experience of.*|skill with.*|skill including.*|understand.*|programming.*\.?$',
            jd[0],
            re.IGNORECASE)
        briefs.append(json.dumps({'brief':brief}))
        year = re.findall(
            r'[0-9].* years.*',
            jd[0],
            re.IGNORECASE)
        years.append(json.dumps({'year':year}))
    for i in range(len(infos)):
        all.append(infos[i]+[briefs[i]]+[years[i]])
    print(all[0])
    print(len(all))
    return all

def save_jd(data):
    sql = "INSERT INTO jd_brief (`job_id`,`position`,`company`,`brief`,`year`) VALUES(%s,%s,%s,%s,%s)"
    back = cursor.executemany(sql, data)  
    connection.commit()
    print('Items save to db: ',back)
# save successfully
# save_jd(job_description())

"""
# too few
cursor.execute("select description from Jobs limit %s",test) 
jds = cursor.fetchall()
for jd in jds:
    salary = re.findall(r'\$.*',jd[0])
    print('salary: ',salary)
"""

def cal_sim():
    # cursor.execute("select description from Joball limit %s",test) 
    cursor.execute("select description from Joball") 
    details = cursor.fetchall()

    skillset = [
        'SQL','Python','Spark','AWS','Java','Hadoop','Hive', 'Scala','Kafka','NoSQL','Redshift','Azure',
        'Linux','R','Tableau','Oracle','Git','Cassandra','Airflow','Snowflake','MySQL','PostgreSQL',
        'C++','MongoDB','GCP','data pipeline','data warehouse','ETL','migration','architectures',
        'distributed','API','Perl','C','Go','agile'
    ]    

    insert_all = []
    cnt = 0
    for detail in details:
        cnt+= 1
        # try:
        skills = re.findall(
            r'years.*|experience.*|skill.*|responsibilities.*|responsibility.*|background.*|understand.*|programming.*',
            detail[0],
            re.IGNORECASE|re.DOTALL)
        # print(cnt) 
        if len(skills) >=1:
            count_skill = [skills[0].count(x) for x in set(skillset)]
            # print('count_skill: ',count_skill)
            insert_all.append(count_skill)
        else:
            count_skill = [-1]
            # print('count_skill: ',count_skill)
            insert_all.append(count_skill) 
    # print('length: ',len(insert_all)) 
    # print(insert_all[0:3])
    id_list = []
    # cursor.execute("select job_id from Joball limit %s",test) 
    cursor.execute("select job_id from Joball") 
    job_ids = cursor.fetchall()
    for id in job_ids:
        id_list.append(id[0])
    # print('job_ids: ',id_list)

    sim = list()
    for i in range(len(insert_all)-1):
        for j in range(len(insert_all)):
            if norm(insert_all[i]) != 0 and norm(insert_all[j]) != 0:
                # print(id_list[i],id_list[j])
                try: 
                    similarity = dot(insert_all[i], insert_all[j])/(norm(insert_all[i]) * norm(insert_all[j]))
                    sim.append([id_list[i],id_list[j],similarity])
                except:
                    similarity = -1
                    sim.append([id_list[i],id_list[j],similarity])
    print('sim: ',len(sim))
    return sim

def save_sim(data):
    # back = cursor.executemany("INSERT INTO skill_sim (job1_id,job2_id,similarity) VALUES(%s,%s,%s)", data) 
    back = cursor.executemany("INSERT INTO recommendations (job1_id,job2_id,similarity) VALUES(%s,%s,%s)", data) 
    connection.commit()
    print('Items save to db: ',back)
# save successfully
# save_sim(cal_sim())


