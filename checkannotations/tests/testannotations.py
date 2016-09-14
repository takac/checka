import ast
import unittest
from checkannotations import checkannotations
from functools import wraps


def ast_from_doc(func):
    @wraps(func)
    def func_wrapper(self):
        tree = ast.parse(func.__doc__)
        attrs = {'__file__': 'madeup/path.py', '__name__': 'mocked'}
        self.mod = type('', (object,), attrs)()
        self.fun = tree.body[0]
        self.checker.check_fn_annotations(self.mod, self.fun)
        return func(self)
    return func_wrapper


class TestCheckAnnotations(unittest.TestCase):

    def setUp(self):
        self.checker = checkannotations.CheckFunction()

    def assertReturnViolation(self):
        self.assertIn({'function': self.fun, 'node': self.fun,
                       'mod': self.mod, 'type': 'return'},
                      self.checker.violations)

    def assertArgViolation(self, arg_no):
        self.assertIn({'function': self.fun,
                       'node': self.fun.args.args[arg_no],
                       'mod': self.mod, 'type': 'arg'},
                      self.checker.violations)

    @ast_from_doc
    def test_check_fn_annotations_ok(self):
        """def annotated_fun(x: int) -> int:
            return x
        """
        self.assertEqual(self.checker.violations, [])

    @ast_from_doc
    def test_check_multi_fn_args_annotations_missing(self):
        """def annotated_fun(x) -> int:
            return x
        """
        self.assertEqual(len(self.checker.violations), 1)
        self.assertArgViolation(0)

    @ast_from_doc
    def test_check_multi_fn_args_annotations_missing_2nd(self):
        """def annotated_fun(x: int, y, z: str, w) -> int:
            return x
        """
        self.assertEqual(len(self.checker.violations), 2)
        self.assertArgViolation(1)
        self.assertArgViolation(3)

    @ast_from_doc
    def test_check_fn_args_annotations_missing(self):
        """def annotated_fun(x, y) -> int:
            return x*y
        """
        self.assertEqual(len(self.checker.violations), 2)
        self.assertArgViolation(0)
        self.assertArgViolation(1)

    @ast_from_doc
    def test_check_fn_return_annotations_missing(self):
        """def missing_return_annotation(x: int, y: int):
            return x*y
        """
        self.assertEqual(len(self.checker.violations), 1)
        self.assertReturnViolation()

    @ast_from_doc
    def test_check_fn_args_with_defaults_annotations_missing(self):
        """def fn_def_args(x=1, y=2) -> int:
            return x*y
        """
        self.assertEqual(len(self.checker.violations), 2)
        self.assertArgViolation(0)
        self.assertArgViolation(1)

    @ast_from_doc
    def test_check_fn_args_ignore_self(self):
        """def fn_def_args(self, y=2) -> int:
            return x*y
        """
        self.assertEqual(len(self.checker.violations), 1)
        self.assertArgViolation(1)
