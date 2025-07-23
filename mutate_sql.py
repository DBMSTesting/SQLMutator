import requests
import json
import re
import ds
import gpt4omini
import llama3
import os
import function_keyword.tidb_keyword
import function_keyword.mysql_keyword
import semantic_validation

mutate_prompt = '''
【Context】You are testing mysql database. We analyzed all the mysql bug reports in the database. For each bug report. Given:
- Bug pattern with placeholders
- Functions/root causes of problems summarized in the bug report
- Feature list

[Task] Generate the SQL test case, the method is as follows:
Step 1: Select high-risk SQL elements that may cause bugs to fill placeholders according to mutation guidance, Mutations do not need to follow the prompts of placeholders, and elements of different types from placeholders but in line with grammatical semantics can also be generated.
Step 2: If there are only SELECT statements, please add DDL (create, alter, drop) and DML (update, insert, delete) statements. If there are only DML statements, please add the table creation statement.
Step 3: Add subqueries, multi-layer nesting, complex logical expressions, implicit type conversions and other functions as much as possible (Not only select statements, all statements need to be added as much as possible). For constants such as function parameters, inserted/changed data, etc., try to generate some extreme constants, such as boundary values, strings containing various uncommon characters, punctuation marks, etc.
Step 4: Add keywords/functions in the function list to the mutation statement group.
PS. Maintain grammatical and semantic correctness(mysql)
PS. Each statement group must contain a create statement and an insert statement. The statements must be complex.

【Output Format】(Output the statements directly, do not use a format similar to ```json, do not use any comments)
{
"sql": "...",
}

【Mutation pattern with placeholders】

'''

epoch_num = 0

db_type = "mysql"

MAX_RETRY = 3
def read_files_in_directory(file_path):
    global epoch_num
    global mutate_prompt

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            filename = file_path.split(os.sep)[-1]
            content = json.load(f)

            mutate_prompt = mutate_prompt
            bug_wait_mutate = content['pattern']
            applied_rule = content['applied_rules']
            affected_elements = content['Affected Elements']
            root_cause = content['Root Cause Analysis']


            # 变异和验证循环
            valid_case = False
            retry_count = 0
            test_case = None


            while not valid_case and retry_count < MAX_RETRY:
                retry_count += 1

                # 1. 生成变异
                response3 = gpt4omini.gpt_api(mutate_prompt + bug_wait_mutate+'\n'+"【Mutation guidance from developers】\n"+"[affected_elements]:"+affected_elements+'\n'+"[root_cause]:"+root_cause+'\n')

                content = response3.choices[0].message.content

                # 提取JSON部分
                pattern = r'\{\s*"sql":\s*".*?"\s*\}'
                matches = re.findall(pattern, content, re.DOTALL)
                if matches:
                    test_case_json = matches[0]
                    try:
                        data = json.loads(test_case_json)
                        test_case = data["sql"]
                    except Exception:
                        test_case = content

                if not test_case:
                    continue

                # 2. 语义验证
                validation_result = semantic_validation.validate_sql_semantics(test_case)

                # 3. 检查验证结果
                if validation_result.get('status') == 'valid':
                    valid_case = True
                    print(f" [Valid] Validation succeeded for {filename} (retry {retry_count})")
                else:
                    print(f" [Retry] Validation failed for {filename} (attempt {retry_count})")

                    # 可选：如果验证失败，添加提示指导后续变异
                    error_details = validation_result.get('potential semantics error', {})
                    error_types = list(error_details.keys()) if isinstance(error_details, dict) else []

                    # 为下一次变异添加错误提示
                    if error_types:
                        mutate_prompt += f"\n\n【Validation Error】The previous mutation was rejected due to: {', '.join(error_types)}. Please correct these issues in your next mutation attempt."

            # 生成结果文件
            if valid_case:
                case_file = f"/mnt/data2/tiancl/project/LlmDBTesting/test_case_suiji/{db_type}/valid_{filename}_{epoch_num}.sql"
                with open(case_file, 'w', encoding='utf-8') as f:
                    f.write(test_case)
                print(f" Saved valid test case: {case_file}")

                # 可选：执行测试
                # dbms_connection.test(db_type, test_case, case_file)
            else:
                print(f" Failed to generate valid test case for {filename} after {MAX_RETRY} attempts")
                # 保存失败的文件用于调试
                case_file = f"/mnt/data2/tiancl/project/LlmDBTesting/test_case_suiji/{db_type}/invalid_{filename}_{epoch_num}.sql"
                with open(case_file, 'w', encoding='utf-8') as f:
                    f.write(test_case)
                    f.write("\n\n--- Validation Errors ---\n")
                    json.dump(validation_result, f, indent=2)
            return test_case

    except Exception as e:
        print(f" Error processing {file_path}: {str(e)}")




test_case = read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/pattern/mysql")