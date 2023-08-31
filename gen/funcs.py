def __get_exchange(tree):
    for child in tree.children:
        if child.data == 'exchange':
            unquoted = child.children[0].value[1:-1]
            return unquoted[0].upper() + unquoted[1:]
        else:
            result = __get_exchange(child)
            if result:
                return result
    return None


def __generate_actor_struct(ast):
    exchange = __get_exchange(ast)
    return ("type {}Actor struct {{\n"
            "\tbroker *volta.App"
            "\n}}\n\n").format(exchange)


def __generate_actor_constructor(ast):
    exchange = __get_exchange(ast)
    return "func New{}Actor(broker *volta.App) *{}Actor {{\n\treturn &{}Actor{{broker: broker}}\n}}\n\n".format(exchange,
                                                                                                            exchange,
                                                                                                            exchange)


def __generate_funcs(ast):
    exchangeName = __get_exchange(ast)

    golang_code = []

    for node in ast.children:
        if node.data == 'action_def':
            for action in node.children[0].children:
                function_name = action.children[0]
                action_arg = action.children[1] if action.children[1] != None else ""

                if action_arg != "":
                    golang_code.append(
                        "func (h *{}Actor) Assign{}Callback(callback func(ctx *volta.Ctx, data {})) error {{"
                        "\n\treturn \n"
                        "}}\n\n".format(exchangeName, function_name, action_arg))
                else:
                    golang_code.append("func (h *{}Actor) Assign{}Callback(callback func(ctx *volta.Ctx)) error {{"
                                       "\n\treturn \n"
                                       "}}\n\n".format(exchangeName, function_name, action_arg))

    return "".join(golang_code)


def generate(ast):
    code = [__generate_actor_struct(ast), __generate_actor_constructor(ast), __generate_funcs(ast)]
    return "".join(code)