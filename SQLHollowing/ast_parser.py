import sqlglot
from sqlglot import expressions as exp


class ASTParser:
    def __init__(self, dialect="mysql"):
        self.dialect = dialect

    def parse(self, sql):
        """将SQL解析为AST"""
        return sqlglot.parse_one(sql, read=self.dialect)

    def generate_sql(self, ast):
        """将AST生成SQL"""
        return ast.sql(dialect=self.dialect, pretty=True)

    def traverse(self, ast):
        """深度优先遍历AST节点"""
        return ast.dfs()