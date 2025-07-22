import pymysql
import clickhouse_connect
# from oceanbase.client import ObClient
import traceback

import duckdb
import sqlite3
import os
import random
import re
import shutil
import json
# import mysql.connector
from clickhouse_driver import Client as ClickHouseClient

pattern = r'(?i)\bCREATE\s+USER\s+[\'"`][^\'"`]+[\'"`]\s+IDENTIFIED\s+BY\s+[\'"`][^\'"`]+[\'"`]'
# pattern_drop = r'(?i)^\s*DROP\s+DATABASE\s+IF\s+EXISTS\s+([`"'\']?[\w-]+[`"'\']?)\s*;?\s*$'
# pattern_create = r'(?i)^\s*CREATE\s+DATABASE\s+([`"\'\]?\w+[`"\']?)\s*;?\s*$'
# pattern_use = r'(?i)^\s*USE\s+([`"\'\]?\w+[`"\']?)\s*;?\s*$'

database_id = 1

db_config = {
    'mysql': {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'port': 3307,
        'database': 'test'
    },
    'tidb': {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'port': 4001,
        'database': 'test'
    },
    'oceanbase': {
        'host': 'localhost',
        'user': 'root',
        'password': 'aikpDpLnObbqMSauOg30',
        'port': 2881,
        'database': 'test'
    },
    'clickhouse': {
        'host': 'localhost',
        'user': 'default',
        'port': 9000,
        'password': '123456',
        'database': 'default'
    }
}

db = "clickhouse"
execute_case = 0
error_case = 0
syntax_error_case = 0
read_only_error_index = 0
lost_connection_error_index = 0
case_num = 0
privilege_index = 0
can_not_connect = 0

def execute_sql(db_type, sql_statements, file_name):
    try:
        if db_type in ['mysql', 'tidb', 'oceanbase']:
            conn = pymysql.connect(
                host=db_config[db_type]['host'],
                user=db_config[db_type]['user'],
                password=db_config[db_type]['password'],
                port=db_config[db_type]['port'],
                # database=db_config[db_type]['database']
            )
            cursor = conn.cursor()
            print("已连接")
            id = str(database_id)
            cursor.execute("DROP DATABASE IF EXISTS database"+id+";")
            cursor.execute("CREATE DATABASE database"+id+";")
            cursor.execute("USE database"+id+";")
            print("建表")
        elif db_type in ['clickhouse']: # clickhouse
            conn = ClickHouseClient(
                host=db_config[db_type]['host'],
                port=db_config[db_type]['port'],
                user=db_config[db_type]['user'],
                password=db_config[db_type]['password'],
            )
            id = str(database_id)
            conn.execute("DROP DATABASE IF EXISTS database"+id+";")
            conn.execute("CREATE DATABASE database"+id+";")
            conn.execute("USE database"+id+";")
        elif db_type in ['duckdb']:
            conn = duckdb.connect(":memory:")
            cursor = conn.cursor()
        elif db_type in ['sqlite']:
            conn = sqlite3.connect("sqlitedatabase/test"+str(database_id)+".db")
            cursor = conn.cursor()
        sql_log = ""
        sql_log = sql_log + str(database_id) + '\n'
        for sql in sql_statements:
            if "read_only" in sql or "READ ONLY" in sql:
                break
            elif re.search(pattern, sql):
                break
            elif "DROP DATABASE" in sql or "drop database" in sql:
                break
            elif "CREATE DATABASE" in sql or "create database" in sql:
                break
            elif sql.startswith("USE ") or sql.startswith("use "):
                break
            elif "sleep" in sql or "SLEEP" in sql:
                break
            elif "memory_limit" in sql:
                break
            elif ("REVOKE" in sql and "PRIVILEGES" in sql) or ("revoke" in sql and "privileges" in sql) or ("revoke" in sql and "PRIVILEGES" in sql) or ("REVOKE" in sql and "privileges" in sql) or ("REVOKE" in sql) or ("revoke" in sql):
                break
            elif "master_pos_wait" in sql:
                break
            elif "s3" in sql:
                break
            # elif "ADMIN SHOW DDL JOBS" in sql:
            #     break
            # elif "_tidb_rowid" in sql:
            #     break
            # elif "s3://" in sql:
            #     break
            
            global execute_case
            execute_case = execute_case + 1
            try:
                if db_type in ['mysql', 'tidb', 'oceanbase', 'duckdb','sqlite']:
                    print(sql)
                    cursor.execute(sql + ";")
                    print(cursor.fetchone())
                    print("执行完毕")
                    sql_log = sql_log + (sql + ";" + "\n\n")
                    # file_name = f"errorstest/{db_type}_error/"+file_name+".txt"
                    # with open(file_name, 'a') as f:
                    #     f.write(sql+"\n\n")
                else:  # clickhouse
                    conn.execute(sql+";")
                    sql_log = sql_log + (sql + ";" + "\n\n")
            except Exception as e:
                global error_case
                error_case = error_case + 1
                if db_type in ['mysql', 'tidb', 'oceanbase']:
                    if "You have an error in your SQL syntax" in str(e):
                        global syntax_error_case
                        syntax_error_case = syntax_error_case + 1
                    elif "The MySQL server is running with the --super-read-only option" in str(e):
                        global read_only_error_index
                        read_only_error_index = 1
                    
                    sql_log = sql_log + ("Error executing SQL:\n"+sql+"\nError Message:"+str(e)+"\n\n")
                elif db_type in ['duckdb','sqlite']:
                    if "syntax error" in str(e):
                        syntax_error_case = syntax_error_case + 1
                    sql_log = sql_log + ("Error executing SQL:\n"+sql+"\nError Message:"+str(e)+"\n\n")
                elif db_type in ['clickhouse']:
                    if "Syntax error" in str(e):
                        syntax_error_case = syntax_error_case + 1
                    sql_log = sql_log + ("Error executing SQL:\n"+sql+"\nError Message:"+str(e)+"\n\n")
        if db_type in ['mysql', 'tidb', 'oceanbase']:
            conn.commit()
            cursor.close()
        if  "Error executing SQL" in sql_log:
            log_error( sql_log, db_type, file_name)
        

        
        # conn.close()
    except Exception as e:
        # global can_not_connect
        # can_not_connect = 1
        if "Lost connection to MySQL server " in str(e):
            global lost_connection_error_index
            lost_connection_error_index = 1
        elif "1044" in str(e):
            global privilege_index
            privilege_index = 1
        # elif "Lost connection to MySQL server during query" in str(e):
        #     global can_not_connect
        #     can_not_connect = 1
        print(str(e))
        print(f"Error connecting to {db_type}: {e}")

def log_error(sql_log, db_type, file_name):
    # log = log + ("Error executing SQL:\n"+sql+"\nError Message:"+error+"\n\n")
    file_name = f"/mnt/data2/tiancl/project/LlmDBTesting/errorstest/suiji/{db_type}/"+file_name
    with open(file_name, 'w') as f:
        # f.write(f"Error executing SQL:\n{sql}\nError Message: {error}\n\n")
        f.write(sql_log)

def test(db_type, test_case, filepath):

    filename = filepath.split(os.sep)[-1]
    sql_statements = test_case.split(';')
    sql_statements = [stmt.strip() for stmt in sql_statements if stmt.strip()]  
    print("开始执行")

    execute_sql(db_type, sql_statements, filename)
    # global database_id
    # database_id = database_id + 1
    
    if execute_case % 100 == 0:
        file_name = f"/mnt/data2/tiancl/project/LlmDBTesting/errorstest/suiji/syntaxAndSemantics/{db_type}.txt"
        with open(file_name, 'a') as f:
            # f.write(f"Error executing SQL:\n{sql}\nError Message: {error}\n\n")
            f.write(str(execute_case) + ' ' + str(syntax_error_case) + ' ' + str(error_case - syntax_error_case) + '\n')
            print(str(execute_case)  + ' ' + str(syntax_error_case) + ' ' + str(error_case - syntax_error_case))


def chuli(dic):
    # processed_dir = os.path.join(dic, "processed_files")
    # os.makedirs(processed_dir, exist_ok=True)
    for root, dirs, files in os.walk(dic):
        # if "processed_files" in dirs:
        #     dirs.remove("processed_files")
        for file in files:
            # # 原始文件路径
            # src_path = os.path.join(root, file)
            # # 目标文件路径
            # dest_path = os.path.join(processed_dir, file)
            # # 检查是否已处理
            # if os.path.exists(dest_path):
            #     print(f"⏩ 已跳过已处理文件: {file}")
            #     continue

            global database_id
            database_id = database_id + 1
            global case_num
            case_num = case_num + 1
            file_path = os.path.join(root, file)
            filename = file_path.split(os.sep)[-1]
            print(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                    # content = json.load(f)
                    # bug_pattern = content['sql']
                    content = f.read()
                    test(db, content, file_path)
                    # shutil.move(src_path, dest_path)
                    # print(f"✅ 已处理并移动文件: {file}")
            
            print(case_num)
            print(execute_case)
            print(error_case)
            print(syntax_error_case)
            if privilege_index == 1:
                break
            elif lost_connection_error_index == 1:
                break
            

if __name__ == "__main__":
    # chuli("/mnt/data2/tiancl/project/LlmDBTesting/test_case/clickhouse")
    chuli("/mnt/data2/tiancl/project/LlmDBTesting/test_case_suiji/clickhouse")
# test(db, statements1, "/mnt/data2/tiancl/project/LlmDBTesting/test_case/test/"+db+"/testcase1")
# test(db, statements2, "/mnt/data2/tiancl/project/LlmDBTesting/test_case/test/"+db+"/testcase2")
# test(db, statements3, "/mnt/data2/tiancl/project/LlmDBTesting/test_case/test/"+db+"/testcase3")
# test(db, statements4, "/mnt/data2/tiancl/project/LlmDBTesting/test_case/test/"+db+"/testcase4")
# test(db, statements5, "/mnt/data2/tiancl/project/LlmDBTesting/test_case/test/"+db+"/testcase5")



