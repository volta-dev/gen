from gen.parser import parser
from gen.shared import get_exchange


class Typer:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # generate constants for the actor
    def __generate_constants(self):
        exchange_name = get_exchange(self.ast)

        golang_code = ["\n// Constants Section\n"]

        #  exchange name const
        golang_code.append("const {}Exchange = \"{}\"\n".format(exchange_name[:1].lower() + exchange_name[1:], exchange_name[0].lower() + exchange_name[1:]))

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]
                    routing_key = action.children[3][1]
                    golang_code.append("const {}{} = {}\n".format(exchange_name[:1].lower() + exchange_name[1:], function_name, routing_key))

        return "".join(golang_code)

    # generate callback type for the actor
    def __generate_callback_type(self):
        exchange_name = get_exchange(self.ast)

        golang_code = ["\n// Callback Type Section\n"]

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]
                    action_arg = action.children[1] if action.children[1] is not None else ""
                    return_arg = action.children[2] if action.children[2] is not None else ""

                    if action_arg != "":
                        action_arg = "data " + action_arg

                    golang_code.append("type {}{}Callback func({}) {}\n".format
                                       (exchange_name, function_name, action_arg, return_arg))

        golang_code.append("\n")

        return "".join(golang_code)

    # generate generates the entire types
    def generate(self):
        code = [self.__generate_constants(), self.__generate_callback_type()]
        return "".join(code)