import ast
import importlib
import sys
from typing import Generator, Callable, Any, Dict, cast
import os

DEBUG = False


def log_violation(fmt_dict: Dict[str, Any]) -> None:
    if fmt_dict['type'] == 'return':
        log_return_violation(fmt_dict)
    elif fmt_dict['type'] == 'argument':
        log_arg_violation(fmt_dict)


def log_arg_violation(fmt_dict: Dict[str, Any]) -> None:
    error('{file_path}:{line_no} A001 Missing annotation for {type} "{name}" '
          'in function "{scope}"'.format(**fmt_dict))


def log_return_violation(fmt_dict: Dict[str, Any]) -> None:
    error('{file_path}:{line_no} A002 Missing annotation for {type} '
          'in function "{scope}"'.format(**fmt_dict))


def error(log: str) -> None:
    print(log)


def log(log: str) -> None:
    if DEBUG:
        print(log)


def file_finder(path: str) -> Generator[str, None, None]:
    if path.endswith(".py"):
        yield path
    elif os.path.isdir(path):
        yield from find_py_files(path)
    else:
        module = importlib.import_module(path)
        if module.__file__.endswith("__init__.py"):
            dirname = os.path.dirname(module.__file__)
            yield from find_py_files(dirname)
        else:
            yield module.__file__


def walk_files(path: str, filter_fun: Callable) -> Generator[str, None, None]:
    yield from (os.path.join(t[0], f)
                for t in os.walk(path) if t[2]
                for f in t[2] if filter_fun(f))


def find_py_files(path: str) -> Generator[str, None, None]:
    yield from walk_files(path,
                          lambda f: f.endswith(".py") and f != '__init__.py')


def walk_ast(root: ast.AST, filter_fun: Callable) -> Generator[
        ast.AST, None, None]:
    for i in ast.iter_child_nodes(root):
        yield from walk_ast(i, filter_fun)
        if filter_fun(i):
            yield i


def find_funcs(root: ast.AST) -> Generator[ast.FunctionDef, None, None]:
    # nasty cast for type checker
    yield from map(lambda f: cast(ast.FunctionDef, f),
                   walk_ast(root, lambda n: type(n) is ast.FunctionDef))


def check_fn_annotations(file_path: str, fun: ast.FunctionDef) -> Generator[
        Dict[str, Any], None, None]:
    args = fun.args.args
    log('Checking function "{}"'.format(fun.name))
    for idx, a in enumerate(args):
        if idx == 0 and a.arg == 'self':
            continue
        log('Checking argument "{}" in function "{}"'.format(a.arg, fun.name))
        annotation = getattr(a, 'annotation')
        if annotation is None:
            yield {'file_path': file_path, 'line_no': a.lineno,
                   'scope': fun.name, 'node': a, 'type': 'argument',
                   'name': a.arg}
    if fun.returns is None:
        yield {'file_path': file_path, 'line_no': fun.lineno,
               'scope': fun.name, 'node': fun, 'type': 'return',
               'name': 'return'}


def check_path(file_path: str) -> int:
    files_to_funs = ((py_file, find_funcs(ast.parse(open(py_file).read())))
                     for py_file in file_finder(file_path))

    y = (violation
         for file, funs in files_to_funs
         for fun in funs
         for violation in check_fn_annotations(file, fun))

    i = None
    for i in y:
        log_violation(i)

    return False if i else True

def main() -> None:
    paths = sys.argv[1:]
    sys.exit(not all(list(map(check_path, paths or ["."]))))

if __name__ == "__main__":
    main()
