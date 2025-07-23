import mutate_sql
import dbms_connection

def main():
    db_type = ""
    filepath = "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/pattern/mysql"
    test_case = mutate_sql.read_files_in_directory(filepath)
    dbms_connection.test(db_type, test_case, filepath)

main()