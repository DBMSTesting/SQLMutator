import json
import os
def read_files_in_directory(directory_path):
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            filename = file_path.split(os.sep)[-1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    bug_wait_mutate = content['pattern']
                    applied_rule = content['applied_rules']
                    affected_elements = content['Affected Elements']
                    root_cause = content['Root Cause Analysis']
                    print(content)
                    print(bug_wait_mutate)
                    print(applied_rule)
                    print(affected_elements)
                    print(root_cause)
            except Exception as e:
                print(f"无法读取文件 {file_path}: {e}")

read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/pattern/json_test")