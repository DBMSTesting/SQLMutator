import gpt4omini
import re
import json


def validate_sql_semantics(sql_test_case: str) -> dict:
    """验证SQL语义的正确性

    Args:
        sql_test_case (str): 包含DDL/DML/DQL的SQL测试用例

    Returns:
        dict: 大模型处理结果（包含元数据和验证状态）
    """
    # 定义语义验证提示
    semantic_validation_prompt = '''
    Role: Unified SQL Semantic Inspector  
    Perform metadata extraction and semantic validation with dynamic rule expansion.

    [Step 1: Metadata Extraction]
    Analyze ALL DDL statements to extract:  
    - Tables: [table1, table2]  
    - Columns per table: {"table1": [col1, col2], ...}  
    - Data types: {"table1.col1": "INT NOT NULL", ...}  
    - Constraints: [PRIMARY KEY(col1), CHECK(col2>0), ...]  
    - Indexes: {"idx1": {"table": "table1", "columns": ["col1"], "type": "BTREE"}} 

    [Step 2: Semantic Validation] 
    Using extracted metadata, verify each DML/DQL statement:  
    1. Column Integrity 
       - Detect missing columns
       - Validate the existence of tables and columns
       - Validate the scope of subqueries
    2. Type Safety  
       - Detect type mismatches in expressions
       - Check for calculation errors in expressions
    3. Constraint Violations  
       - Check for primary key violations
       - Validate foreign key references 
       - Check unique constraints
       - Validate non-null constraints
       - Validate CHECK constraints
    4. Index Consistency inspector 
       - Verify operations on non-existent indexes

    [Dynamic Rule Expansion Protocol]
    IF encounter new error type NOT in [1-4]:
    ADD new check item with format: <Error description>: <Example>

    [Output Protocol] 
    Valid Case:  {"status": "valid", "metadata": {...}}
    Not Valid Case:  {"status": "not valid", "potential semantics error": {...}, "metadata": {...}}
    '''

    # 构建完整提示
    full_prompt = f"{semantic_validation_prompt}\n\n--- SQL TEST CASE ---\n{sql_test_case}"

    try:
        # 调用您的gpt_api函数
        response = gpt4omini.gpt_api(full_prompt)

        # 从响应中提取内容
        model_output = response.choices[0].message.content

        # 尝试解析JSON输出
        try:
            # 使用正则表达式提取可能的JSON部分
            json_match = re.search(r'\{.*\}', model_output, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # 如果没有找到JSON，尝试直接解析整个响应
                return json.loads(model_output.strip())
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Failed to parse model output as JSON",
                "raw_response": model_output
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}