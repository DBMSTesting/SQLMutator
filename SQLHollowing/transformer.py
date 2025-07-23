from .ast_parser import ASTParser
from .hollowing_rules import HollowingRules


class ASTHollowingTransformer:
    def __init__(self, max_hollows=3, dialect="mysql"):
        self.max_hollows = max_hollows
        self.parser = ASTParser(dialect)
        self.hollow_count = 0

    def apply_hollowing(self, sql):
        """主入口：应用空心化转换"""
        ast = self.parser.parse(sql)
        self.hollow_count = 0
        self._hollow_ast(ast)
        return self.parser.generate_sql(ast)

    def _hollow_ast(self, node):
        """递归应用空心化规则"""
        if self.hollow_count >= self.max_hollows:
            return

        # 检查当前节点适用的规则
        for rule in HollowingRules.get_rules_by_type(type(node)):
            rule["action"](node)
            self.hollow_count += 1
            if self.hollow_count >= self.max_hollows:
                return

        # 递归处理子节点
        for child in node.args.values():
            if isinstance(child, (list, tuple)):
                for item in child:
                    if isinstance(item, exp.Expression):
                        self._hollow_ast(item)
            elif isinstance(child, exp.Expression):
                self._hollow_ast(child)