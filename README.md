# Annotation Checker

`mypy` now provides type checking in python using annotations on types, and
there are several packages now that enforce the types are correct at runtime.
However this only works if types are applied throughout the project.

This project aims to check your project and notify you when you forget to add an
annotation.

If type annotations are successfully provided throughout the project then
`mypy` and other analysis tools can become very powerful additions to
your project.

## Install
```bash
git clone https://github.com/takac/checka
cd checka
pip install -e .
```

## Usage
```bash
checka mymodule/mydir
```

Output:
```text
madeup/path.py:1 Missing annotation from function: "mocked.fn_def_args" for argument "y"
madeup/path.py:5 Missing annotation from function: "mocked.missing_return_annotation" for return
madeup/path.py:12 Missing annotation from function: "mocked.annotated_fun" for argument "x"
madeup/path.py:12 Missing annotation from function: "mocked.annotated_fun" for argument "y"
madeup/path.py:12 Missing annotation from function: "mocked.annotated_fun" for argument "w"
```

## Development
- Only supports checking functions for annotations
- Must pass direct module path

