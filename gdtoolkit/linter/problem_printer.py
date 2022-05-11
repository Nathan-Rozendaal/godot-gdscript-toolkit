import sys
from .problem import Problem


def print_problem(problem: Problem, file_path: str) -> None:  # TODO: colors
    print(
        "::error file={},line={},col={}::{}".format(
            file_path,
            problem.line,
            problem.column,
            problem.description
        ),
        file=sys.stderr,
    )
    # print(file_lines[problem.line-1], file=sys.stderr)
    # print('{}^'.format(' ' * problem.column)) # TODO: underline range instead
