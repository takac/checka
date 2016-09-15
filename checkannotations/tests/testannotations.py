import ast
import unittest
from checkannotations import checkannotations
from functools import wraps


def ast_from_doc(func):
    @wraps(func)
    def func_wrapper(self):
        tree = ast.parse(func.__doc__)
        self.fun = tree.body[0]
        self.file_path = 'madeup/path.py'
        self.violations = list(
            checkannotations.check_fn_annotations(self.file_path, self.fun))
        return func(self)
    return func_wrapper


class TestCheckAnnotations(unittest.TestCase):

    def assertReturnViolation(self):
        self.assertIn({'scope': self.fun.name, 'node': self.fun,
                       'file_path': self.file_path,
                       'line_no': self.fun.lineno, 'type': 'return',
                       'name': 'return'}, self.violations)

    def assertArgViolation(self, arg_no):
        self.assertIn({'scope': self.fun.name,
                       'node': self.fun.args.args[arg_no],
                       'file_path': self.file_path, 'type': 'argument',
                       'name': self.fun.args.args[arg_no].arg,
                       'line_no': self.fun.args.args[arg_no].lineno},
                      self.violations)

    @ast_from_doc
    def test_check_fn_annotations_ok(self):
        """def annotated_fun(x: int) -> int:
            return x
        """
        self.assertEqual(self.violations, [])

    @ast_from_doc
    def test_check_multi_fn_args_annotations_missing(self):
        """def annotated_fun(x) -> int:
            return x
        """
        self.assertEqual(len(self.violations), 1)
        self.assertArgViolation(0)

    @ast_from_doc
    def test_check_multi_fn_args_annotations_missing_2nd(self):
        """def annotated_fun(x: int, y, z: str, w) -> int:
            return x
        """
        self.assertEqual(len(self.violations), 2)
        self.assertArgViolation(1)
        self.assertArgViolation(3)

    @ast_from_doc
    def test_check_fn_args_annotations_missing(self):
        """def annotated_fun(x, y) -> int:
            return x*y
        """
        self.assertEqual(len(self.violations), 2)
        self.assertArgViolation(0)
        self.assertArgViolation(1)

    @ast_from_doc
    def test_check_fn_return_annotations_missing(self):
        """def missing_return_annotation(x: int, y: int):
            return x*y
        """
        self.assertEqual(len(self.violations), 1)
        self.assertReturnViolation()

    @ast_from_doc
    def test_check_fn_args_with_defaults_annotations_missing(self):
        """def fn_def_args(x=1, y=2) -> int:
            return x*y
        """
        self.assertEqual(len(self.violations), 2)
        self.assertArgViolation(0)
        self.assertArgViolation(1)

    @ast_from_doc
    def test_check_fn_args_ignore_self(self):
        """def fn_def_args(self, y=2) -> int:
            return x*y
        """
        self.assertEqual(len(self.violations), 1)
        self.assertArgViolation(1)
