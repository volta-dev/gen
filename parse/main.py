from lark import Lark, Transformer, Tree

dsl_grammar = """
    start: exchange? type_def action_def
    exchange: "exchange" "=" ESCAPED_STRING
    type_def: "types" "{" type_body "}"
    action_def: "actions" "{" action_body "}"
    type_body: type_entry+
    action_body: action_entry+
    type_entry: CNAME "{" param_def+ "}"
    action_entry: CNAME "(" CNAME? ")" CNAME metadata?
    param_def: CNAME CNAME metadata?
    metadata: "@" CNAME routing_key?
    routing_key: "(" ESCAPED_STRING ")" 
    %import common.CNAME
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""


class MyTransformer(Transformer):
    def exchange(self, args):
        return Tree('exchange', args)

    def start(self, args):
        return Tree('start', args)

    def type_def(self, args):
        return Tree('type_def', args)

    def action_def(self, args):
        return Tree('action_def', args)

    def type_body(self, args):
        return Tree('type_body', args)

    def action_body(self, args):
        return Tree('action_body', args)

    def type_entry(self, args):
        return Tree('type_entry', [args[0], Tree('params', args[1:])])

    def action_entry(self, args):
        if len(args) > 3:
            return Tree('action_entry', [args[0], args[1], args[2], args[3]])

        return Tree('action_entry', [args[0], None, args[2], args[3] if len(args) > 3 else None])

    def param_def(self, args):
        return Tree('param_def', [args[0], args[1], args[2] if len(args) > 2 else None])

    def metadata(self, args):
        return Tree('metadata', args)

    def routing_key(self, args):
        return args[0]


def parser(data):
    return Lark(dsl_grammar, parser='lalr', transformer=MyTransformer()).parse(data)

