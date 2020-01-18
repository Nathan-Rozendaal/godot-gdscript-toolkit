from typing import List

from lark import Tree

from .types import Node
from .expression_utils import is_any_comma, is_any_parentheses, has_leading_dot


def expression_to_str(expression: Node) -> str:
    if isinstance(expression, Tree):
        return {
            "assnmnt_expr": _operator_chain_based_expression_to_str,
            "test_expr": _operator_chain_based_expression_to_str,
            "or_test": _operator_chain_based_expression_to_str,
            "and_test": _operator_chain_based_expression_to_str,
            "not_test": lambda e: "{} {}".format(
                expression_to_str(e.children[0]), expression_to_str(e.children[1])
            ),
            "content_test": _operator_chain_based_expression_to_str,
            "comparison": _operator_chain_based_expression_to_str,
            "bitw_or": _operator_chain_based_expression_to_str,
            "bitw_xor": _operator_chain_based_expression_to_str,
            "bitw_and": _operator_chain_based_expression_to_str,
            "shift_expr": _operator_chain_based_expression_to_str,
            "subtr_expr": _operator_chain_based_expression_to_str,
            "addn_expr": _operator_chain_based_expression_to_str,
            "mdr_expr": _operator_chain_based_expression_to_str,
            "neg_expr": lambda e: "-{}".format(expression_to_str(e.children[1])),
            "bitw_not": lambda e: "~{}".format(expression_to_str(e.children[1])),
            "type_test": _operator_chain_based_expression_to_str,
            "type_cast": _operator_chain_based_expression_to_str,
            "standalone_call": _standalone_call_to_str,
            "getattr_call": _getattr_call_to_str,
            "getattr": lambda e: ".".join([expression_to_str(c) for c in e.children]),
            "subscr_expr": _subscription_to_str,
            "par_expr": lambda e: "({})".format(expression_to_str(e.children[0])),
            "array": _array_to_str,
            "dict": _dict_to_str,
            "c_dict_element": _dict_element_to_str,
            "eq_dict_element": _dict_element_to_str,
            "string": lambda e: e.children[0].value,
            "node_path": lambda e: "@{}".format(expression_to_str(e.children[0])),
            "get_node": lambda e: "${}".format(expression_to_str(e.children[0])),
            "path": lambda e: "/".join([name_token.value for name_token in e.children]),
        }[expression.data](expression)
    return expression.value


def _operator_chain_based_expression_to_str(expression: Tree) -> str:
    operator_expr_chain = zip(expression.children[1::2], expression.children[2::2])
    chain = [
        " {} {}".format(expression_to_str(operator), expression_to_str(expr))
        for operator, expr in operator_expr_chain
    ]
    first_expr = expression.children[0]
    return "{}{}".format(expression_to_str(first_expr), "".join(chain))


def _standalone_call_to_str(call: Tree) -> str:
    is_super_call = False
    offset = 0
    if has_leading_dot(call):
        is_super_call = True
        offset = 1

    super_prefix = "." if is_super_call else ""
    callee = expression_to_str(call.children[0 + offset])
    arguments = _arguments_to_str(call.children[1 + offset :])
    return "{}{}({})".format(super_prefix, callee, arguments)


def _getattr_call_to_str(call: Tree) -> str:
    a_getattr = expression_to_str(call.children[0])
    arguments = _arguments_to_str(call.children[1:])
    return "{}({})".format(a_getattr, arguments)


def _arguments_to_str(arguments: List[Node]) -> str:
    return ", ".join(
        [
            expression_to_str(argument)
            for argument in arguments
            if not is_any_parentheses(argument) and not is_any_comma(argument)
        ]
    )


def _array_to_str(array: Tree) -> str:
    elements = [
        expression_to_str(child) for child in array.children if not is_any_comma(child)
    ]
    return "[{}]".format(", ".join(elements))


def _dict_to_str(a_dict: Tree) -> str:
    elements = [expression_to_str(child) for child in a_dict.children]
    return "{{{}}}".format(", ".join(elements))


def _subscription_to_str(subscription: Tree) -> str:
    return "{}[{}]".format(
        expression_to_str(subscription.children[0]),
        expression_to_str(subscription.children[1]),
    )


def _dict_element_to_str(dict_element: Tree) -> str:
    template = "{}: {}" if dict_element.data == "c_dict_element" else "{} = {}"
    return template.format(
        expression_to_str(dict_element.children[0]),
        expression_to_str(dict_element.children[1]),
    )
