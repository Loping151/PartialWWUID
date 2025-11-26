from gsuid_core.logger import logger


def convert_wrapper(func):
    def wrapper(a, b):
        def convert(value):
            if isinstance(value, str):
                if "%" in value:
                    value.replace("%", "")
                try:
                    value = float(value)
                except ValueError as _:
                    pass
            elif isinstance(value, list):
                return [convert(item) for item in value]
            return value

        a = convert(a)
        b = convert(b)
        return func(a, b)

    return wrapper


class ExpressionFunc:
    @staticmethod
    def func_equal(a, b):
        return a == b

    @staticmethod
    def func_not_equal(a, b):
        return a != b

    @staticmethod
    @convert_wrapper
    def func_less_than(a, b):
        return a < b

    @staticmethod
    @convert_wrapper
    def func_greater_than(a, b):
        return a > b

    @staticmethod
    @convert_wrapper
    def func_less_than_or_equal(a, b):
        return a <= b

    @staticmethod
    @convert_wrapper
    def func_greater_than_or_equal(a, b):
        return a >= b

    @staticmethod
    @convert_wrapper
    def func_in(a, b):
        if isinstance(a, list):
            return any(i in b for i in a)

        return a in b

    @staticmethod
    @convert_wrapper
    def func_not_in(a, b):
        if isinstance(a, list):
            return all(i not in b for i in a)
        return a not in b


class ExpressionEvaluator:
    def __init__(self, ctx):
        self.ctx = ctx

    def evaluate(self, expression):
        return self._evaluate_expression(expression["op"], expression)

    def _evaluate_expression(self, op, expression):
        if op in {"&&", "||", "!"}:
            return self._evaluate_logical(op, expression["sub"])
        else:
            return self._evaluate_comparison(expression)

    def _evaluate_logical(self, op, childs):
        operations = {
            "&&": all,
            "||": any,
            "!": lambda v: not list(v)[0],
        }
        operation = operations[op]
        return operation(self.evaluate(child) for child in childs)

    def _evaluate_comparison(self, expression):
        operations = {
            "=": ExpressionFunc.func_equal,
            "!=": ExpressionFunc.func_not_equal,
            "<": ExpressionFunc.func_less_than,
            ">": ExpressionFunc.func_greater_than,
            "<=": ExpressionFunc.func_less_than_or_equal,
            ">=": ExpressionFunc.func_greater_than_or_equal,
            "in": ExpressionFunc.func_in,
            "!in": ExpressionFunc.func_not_in,
        }
        key, op, value = expression["key"], expression["op"], expression["value"]
        return operations[op](self.ctx.get(key), value)


def find_first_matching_expression(ctx, expressions, default="calc.json"):
    evaluator = ExpressionEvaluator(ctx)
    for expr in expressions:
        try:
            if evaluator.evaluate(expr):
                return expr["choose"]
        except Exception as e:
            logger.exception(e)
    return default
