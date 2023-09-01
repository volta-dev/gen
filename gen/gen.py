from gen.parser import parser

class Gen:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # generate dto structs
    def __generate_dto(self):
        dto = []

        for node in self.ast.children:
            if node.data == 'type_def':
                for type in node.children[0].children:
                    struct_name = type.children[0]
                    dto.append("type {} struct {{\n".format(struct_name))
                    fields = []

                    for params in type.children[1].children:
                        field_name = params.children[0]
                        field_type = params.children[1]

                        if field_type.lower() == 'string':
                            field_type = 'string'
                        elif field_type.lower() == 'int':
                            field_type = 'int'
                        elif field_type.lower() == 'bool':
                            field_type = 'bool'

                        fields.append((field_name, field_type))
                        dto.append("\t{} {} `json:\"{}\"`\n".format(field_name, field_type, field_name))

                    dto.append("}\n\n")

        return "".join(dto)

    # finds the exchange name in the ast
    def __get_exchange(self, tree):
        for child in tree.children:
            if child.data == 'exchange':
                unquoted = child.children[0].value[1:-1]
                return unquoted[0].upper() + unquoted[1:]
            else:
                result = self.__get_exchange(tree)
                if result:
                    return result
        return None

    # generates the struct for the actor
    def __generate_actor_struct(self):
        exchange = self.__get_exchange(self.ast)
        return ("type {}Actor struct {{\n"
                "\tbroker *volta.App"
                "\n}}\n\n").format(exchange)

    # generates the constructor for the actor
    def __generate_actor_constructor(self):
        exchange = self.__get_exchange(self.ast)
        return "func New{}Actor(broker *volta.App) *{}Actor {{\n\treturn &{}Actor{{broker: broker}}\n}}\n\n".format(
            exchange, exchange, exchange)

    # generate callback type for the actor
    def __generate_callback_type(self):
        exchangeName = self.__get_exchange(self.ast)

        golang_code = []

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]
                    action_arg = action.children[1] if action.children[1] != None else ""
                    return_arg = action.children[2] if action.children[2] != None else ""

                    if action_arg != "":
                        action_arg = "data " + action_arg

                    golang_code.append("type {}{}Callback func({}) {}\n".format
                                       (exchangeName, function_name, action_arg, return_arg))

        return "".join(golang_code)

    # generates the functions for the actor
    def __generate_funcs(self):
        exchangeName = self.__get_exchange(self.ast)

        golang_code = ["\n"]

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]
                    action_arg = action.children[1] if action.children[1] != None else ""
                    return_arg = action.children[2] if action.children[2] != None else ""

                    if action_arg != "":
                        golang_code.append(
                            "func (h *{}Actor) Assign{}Callback(callback func(data {}) {}) {{"
                            "\n\treturn \n"
                            "}}\n\n".format(exchangeName, function_name, action_arg, return_arg))
                    else:
                        golang_code.append("func (h *{}Actor) Assign{}Callback(callback func()) {} {{"
                                           "\n\treturn \n"
                                           "}}\n\n".format(exchangeName, function_name, action_arg, return_arg))

        return "".join(golang_code)

    # generates the entire actor
    def generate(self):
        code = [self.__generate_dto(), self.__generate_actor_struct(), self.__generate_actor_constructor(),
                self.__generate_callback_type(), self.__generate_funcs()]
        return "".join(code)
