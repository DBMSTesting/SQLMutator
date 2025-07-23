from SQLHollowing.transformer import ASTHollowingTransformer

# 示例SQL
sql = """
SELECT name, MAX(salary) 
FROM employees 
WHERE department = 'IT' AND salary > 10000 
GROUP BY department 
HAVING COUNT(*) > 5 
ORDER BY name DESC 
LIMIT 10
"""

# 应用空心化
transformer = ASTHollowingTransformer(max_hollows=3)
hollowed_sql = transformer.apply_hollowing(sql)

print("Original SQL:")
print(sql)
print("\nHollowed SQL:")
print(hollowed_sql)