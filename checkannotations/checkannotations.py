import ast
import importlib
import sys
from typing import Any, List

DEBUG = False


def main(module_name: str) -> int:
    c = CheckFunction()
    c.check_module(module_name)
    if len(c.violations) > 0:
        return -1
    return 0


def error(log: str) -> None:
    print(log)


def log(log: str) -> None:
    if DEBUG:
        print(log)


class CheckFunction(object):

    def __init__(self):
        self.violations = []  # type: List[Dict[str, Any]]

    def check_module(self, module_name: str) -> None:
        module = importlib.import_module(module_name)
        source = module.__file__
        tree = ast.parse(open(source).read())
        funs = []

        class FuncVisiter(ast.NodeVisitor):
            def visit_FunctionDef(self, func: ast.FunctionDef) -> None:
                if func.name is not '__init__':
                    funs.append(func)
                self.generic_visit(func)

        FuncVisiter().visit(tree)

        for fundef in funs:
            self.check_fn_annotations(module, fundef)

    def log_arg_violation(self, mod: Any, fun: ast.FunctionDef,
                          arg: ast.arg) -> None:
        self.violations.append(
                {'mod': mod, 'function': fun, 'node': arg, 'type': 'arg'})
        error('{}:{} Missing annotation from function: "{}.{}" '
              'for argument "{}"'.format(mod.__file__, arg.lineno,
                                         mod.__name__, fun.name, arg.arg))

    def log_return_violation(self, mod: Any, fun: ast.FunctionDef) -> None:
        self.violations.append(
                {'mod': mod, 'function': fun, 'node': fun, 'type': 'return'})
        error('{}:{} Missing annotation from function: "{}.{}" '
              'for return'.format(mod.__file__, fun.lineno,
                                  mod.__name__, fun.name))

    def check_fn_annotations(self, mod: Any, fun: ast.FunctionDef) -> List:
        args = fun.args.args
        log('Checking function "{}"'.format(fun.name))
        for idx, a in enumerate(args):
            if idx == 0 and a.arg == 'self':
                continue
            log('Checking argument "{}" in function "{}"'.format(a.arg,
                                                                 fun.name))
            annotation = getattr(a, 'annotation')
            if annotation is None:
                self.log_arg_violation(mod, fun, a)
        if fun.returns is None:
            self.log_return_violation(mod, fun)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
