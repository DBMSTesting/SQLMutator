import requests
import json
import re
import ds
import gpt4omini
# import llama3
# import llama3
import os
import dbms_connection
import function_keyword.tidb_keyword
import function_keyword.mysql_keyword
import function_keyword.oceanbase_keyword
import function_keyword.sqlite_keyword
import function_keyword.duckdb_keyword
import function_keyword.clickhouse_keyword
import concurrent.futures


epoch_num = 0  
def process_file(file_path, db_type):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    filename = file_path.split(os.sep)[-1]
                    content = json.load(f)
                    
                    bug_wait_mutate = content['pattern']
                    applied_rule = content['applied_rules']
                    affected_elements = content['Affected Elements']
                    root_cause = content['Root Cause Analysis']


                    # mutation_candidate = mutation_candidates(applied_rule)
                    if db_type == "mysql":
                        mutation_candidate = function_keyword.mysql_keyword.choose_keyword()
                    elif db_type == "oceanbase":
                        mutation_candidate = function_keyword.oceanbase_keyword.choose_keyword()
                    elif db_type == "sqlite":
                        mutation_candidate = function_keyword.sqlite_keyword.choose_keyword()
                    elif db_type == "duckdb":
                        mutation_candidate = function_keyword.duckdb_keyword.choose_keyword()
                    elif db_type == "tidb":
                        mutation_candidate = function_keyword.tidb_keyword.choose_keyword()
                    elif db_type == "clickhouse":
                        mutation_candidate = function_keyword.clickhouse_keyword.choose_keyword()
                    

                    print(mutation_candidate)
                    # response3 = gpt4omini.gpt_api(mutate_prompt+bug_wait_mutate+'\n'+"【Mutation guidance from developers】\n"+"[affected_elements]:"+affected_elements+'\n'+"[root_cause]:"+root_cause+'\n'+"【Feature list】\n"+mutation_candidate +'\n')
                    # response3 = llama3.llama_api(mutate_prompt+bug_wait_mutate+'\n'+"【Mutation guidance from developers】\n"+"[affected_elements]:"+affected_elements+'\n'+"[root_cause]:"+root_cause+'\n'+"【Feature list】\n"+mutation_candidate +'\n')
                    response3 = gpt4omini.gpt_api(mutate_prompt_suiji + bug_wait_mutate)
                    content = response3.choices[0].message.content
                    pattern = r'\{\s*"sql":\s*".*?"\s*\}'
                    # print(content)

                    # 第一步：过滤所有<think>标签内容（包括嵌套花括号）
                    # cleaned_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
                    # print(cleaned_content)

                    # 查找 JSON 部分
                    # json_match = re.search(r'(\{.*?"sql":.*?\})', cleaned_content)
                    # # 第二步：匹配第一个完整JSON对象
                    # json_str = json_match.group(1)
                    matches = re.findall(pattern, content, re.DOTALL)
                    for match in matches:
                        content = match
                        break
                    data = json.loads(content)
                    # data = json.loads(content)
                    test_case = data["sql"]

                    # content3 = response3.get("message", {}).get("content", "")
                    # json_block3 = re.search(r'```json\n(.*?)\n```', content3, re.DOTALL)
                    # parsed3 = json.loads(json_block3.group(1))
                    # answer_list = parsed3.get("mutations", [])
                    # first_answer = answer_list[0]
                    # test_case = first_answer.get("sql","")

                    case_file = "/mnt/data2/tiancl/project/LlmDBTesting/test_case_suiji/"+db_type+"/"+filename+str(epoch_num)
                    with open(case_file, 'w', encoding='utf-8') as f:
                        f.write(test_case)

                    # dbms_connection.test(db_type, test_case, case_file)

                    
                    
            except Exception as e:
                print(f"{e}")     

def read_files_in_directory(directory_path, db_type):
    while True:
        global epoch_num
        epoch_num = epoch_num + 1
        if not os.path.exists(directory_path):
            print(f"目录 {directory_path} 不存在")
            return
    
        # for root, dirs, files in os.walk(directory_path):
        #     for file in files:
        #         file_path = os.path.join(root, file)
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:  
            futures = []
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    futures.append(executor.submit(process_file, file_path, db_type))
        
            # 获取处理结果
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    # 处理或存储结果
                    print(f"Processed: {result['filename']}")
        
                

# candidate_map = {
#     "select_parameter": ["agg", "column", "distinct", "all", "any", "constant"],
#     "from_parameter": ["table", "join"],

# }

def mutation_candidates(applied_rules):
    mutation_candidate = "Optional mutation elements:\n"
    for rule in applied_rules:
        if rule in candidate_map:
            mutation_candidate = mutation_candidate+rule+":"+applied_rules[rule]+'\n'
    return mutation_candidate


# mutate_prompt = '''
# 【Context】You are testing a SQL database. We analyzed all the mysql bug reports in the database. For each bug report. Given:
# - Mutation statement pattern with placeholders (test cases in the bug report are hollowed out)
# - Functions/root causes of problems summarized in the bug report
# - Feature list (indicates elements that can be selected to fill placeholders)

# [Task] Generate the SQL test case, the method is as follows:
# 1. Select high-risk SQL elements that may cause bugs to fill placeholders according to mutation guidance
# 2. Maintain grammatical and semantic correctness(mysql)
# 3. Some keywords/functions are prompted in the feature list, and the generated test cases need to include these functions to increase the complexity of the statements

# [Generation principles]
# 1. Add subqueries, multi-layer nesting, complex logical expressions, implicit type conversions and other functions as much as possible (in addition to select statements, other statements should also be added to make the statements as complex as possible)
# 2. Mutations do not need to follow the prompts of placeholders, and elements of different types from placeholders but in line with grammatical semantics can also be generated
# 3. For constants such as function parameters, inserted/changed data, etc., try to generate some extreme constants, such as boundary values, strings containing various uncommon characters, punctuation marks, etc.
# 4. Some statements may only contain select statements. You need to complete some DDL (create, alter, drop) and DML (update, insert, delete) statements while ensuring the correct syntax and semantics.
# 【Output Format】(Output the result directly, do not use a format similar to ```json)
# {
# "sql": "...",
# }

# 【Mutation pattern with placeholders】

# '''

mutate_prompt = '''
【Context】You are testing  database. We analyzed all the oceanbase bug reports in the database. For each bug report. Given:
- Bug pattern with placeholders
- Functions/root causes of problems summarized in the bug report

[Task] Generate the SQL test case, the method is as follows:
Rule 1: Select high-risk SQL elements that may cause bugs to fill placeholders according to mutation guidance, Mutations do not need to follow the prompts of placeholders, and elements of different types from placeholders but in line with grammatical semantics can also be generated.
Rule 2: Each statement must contain multiple levels of nested subqueries and complex logical expressions (Not only select statements, all statements need to be added as much as possible). For constants such as function parameters, inserted/changed data, etc., try to generate some extreme constants, such as boundary values, strings containing various uncommon characters, punctuation marks, etc.

【Output Format】(Output the statements directly, do not use a format similar to ```json or ```sql, do not use any comments, do not output any other content except for the JSON format below)
{
"sql": "..."
}

【Mutation pattern with placeholders】

'''

mutate_prompt_suiji = '''
Please mutate this SQL pattern into a oceanbase test case. You can mutate it randomly, but don't make it too similar to the original statement. You don't need to mutate based on placeholders, and you can drastically change the statement structure and content. The mutation should be strong, not just a few minor changes.
【Output Format】(Output the statements directly, do not use a format similar to ```json or ```sql, do not use any comments, do not output any other content except for the JSON format below)
{
"sql": "..."
}

【Mutation pattern with placeholders】

'''

read_files_in_directory("/mnt/data2/tiancl/project/LlmDBTesting/pattern/oceanbase", "oceanbase")


