from sqlglot import expressions as exp


class HollowingRules:
    RULES = {
        # DQL规则
        "DQL_01": {
            "description": "Replace keyword parameters",
            "node_type": exp.Select,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<selectpara>")])
        },
        "DQL_02": {
            "description": "Replace function parameters",
            "node_type": exp.Func,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<funcpara>")])
        },
        "DQL_03": {
            "description": "Replace operator parameters",
            "node_type": exp.Binary,
            "action": lambda node: node.set("expression", exp.Identifier(this="<operatorpara>"))
        },
        "DQL_04": {
            "description": "Replace operators",
            "node_type": exp.Binary,
            "action": lambda node: node.replace(exp.Identifier(this="<operator>"))
        },
        "DQL_05": {
            "description": "Replace join operator",
            "node_type": exp.Join,
            "action": lambda node: node.set("on", exp.Identifier(this="<joincond>"))
        },

        # DML规则
        "DML_07": {
            "description": "Replace insert parameters",
            "node_type": exp.Insert,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<insertval>")])
        },
        "DML_08": {
            "description": "Replace update parameters",
            "node_type": exp.Update,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<updateval>")])
        },

        # DDL规则 (扩展实现)
        "DDL_10": {
            "description": "Replace data type",
            "node_type": exp.DataType,
            "action": lambda node: node.replace(exp.Identifier(this="<datatype>"))
        },
        "DDL_11": {
            "description": "Replace constraint type",
            "node_type": exp.Constraint,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<constraint>")])
        },
        "DDL_12": {
            "description": "Replace index type",
            "node_type": exp.Index,
            "action": lambda node: node.set("expressions", [exp.Identifier(this="<indextype>")])
        },

        # 扩展规则
        "EXT_01": {
            "description": "Replace WHERE condition",
            "node_type": exp.Where,
            "action": lambda node: node.set("this", exp.Identifier(this="<wherecond>"))
        },
        "EXT_02": {
            "description": "Replace LIMIT clause",
            "node_type": exp.Limit,
            "action": lambda node: node.set("expression", exp.Identifier(this="<limitval>"))
        }
    }

    @classmethod
    def get_rule(cls, rule_id):
        return cls.RULES.get(rule_id)

    @classmethod
    def get_rules_by_type(cls, node_type):
        return [rule for rule in cls.RULES.values() if rule["node_type"] == node_type]