from gen.parser import parser
from gen.shared import get_exchange


class Actor:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # generates the struct for the actor
    def __generate_actor_struct(self):
        exchange_name = get_exchange(self.ast)
        golang_code = ["type {}Actor struct {{\n".format(exchange_name), "\tbroker *volta.App\n\n"]

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]

                    golang_code.append("\t{}{}Callback {}{}Callback\n".format
                                       (exchange_name[0].lower() + exchange_name[1:], function_name, exchange_name,
                                        function_name))

        golang_code.append("}\n\n")

        return "".join(golang_code)

    # generates the constructor for the actor
    def __generate_actor_constructor(self):
        exchange = get_exchange(self.ast)
        return "func New{}Actor(broker *volta.App) *{}Actor {{\n\treturn &{}Actor{{broker: broker}}\n}}\n\n".format(
            exchange, exchange, exchange)

    # generate the init function for exchange and queues
    def __generate_init(self):
        exchange_name = get_exchange(self.ast)

        golang_code = ["func (actor *{}Actor) Init() {{\n".format(exchange_name),
                       "\tactor.broker.AddExchanges(volta.Exchange{{Name: \"{}\", Type: \"topic\"}})\n\n".format(
                           exchange_name[0].lower() + exchange_name[1:])]

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    routing_key = action.children[3][1]
                    golang_code.append(
                        "\tactor.broker.AddQueue(volta.Queue{{Name: {}, RoutingKey: {}, Exchange: \"{}\"}})\n".format(
                            routing_key,
                            routing_key, exchange_name[0].lower() + exchange_name[1:]))

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    routing_key = action.children[3][1]
                    func_arg = action.children[1] if action.children[1] is not None else ""
                    return_arg = action.children[2] if action.children[2] is not None else ""

                    if func_arg == "" and return_arg == "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\tactor.{}{}Callback()\n"
                                           "\t\treturn ctx.Ack(false)\n"
                                           "\t}})\n".format(routing_key, exchange_name[0].lower() + exchange_name[1:],
                                                            action.children[0]))
                    elif func_arg == "" and return_arg != "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\treturn ctx.ReplyJSON(actor.{}{}Callback())\n"
                                           "\t}})\n".format(routing_key, exchange_name[0].lower() + exchange_name[1:],
                                                            action.children[0]))
                    elif func_arg != "" and return_arg == "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\tvar data _internal{}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           "\t\tactor.{}{}Callback({}FromInternal(data))\n"
                                           "\t\treturn ctx.Ack(false)\n"
                                           "\t}})\n".format(routing_key, action.children[1],
                                                            exchange_name[0].lower() + exchange_name[1:],
                                                            action.children[0],
                                                            action.children[1][:1].lower() + action.children[1][1:]))
                    elif func_arg != "" and return_arg != "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\tvar data _internal{}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           "\t\treturn ctx.ReplyJSON(actor.{}{}Callback({}FromInternal(data)))\n"
                                           "\t}})\n".format(routing_key, action.children[1],
                                                            exchange_name[0].lower() + exchange_name[1:],
                                                            action.children[0],
                                                            action.children[1][:1].lower() + action.children[1][1:]))

        golang_code.append("}\n\n")

        return "".join(golang_code)

    # generates the functions for the actor
    def __generate_funcs(self):
        exchangeName = get_exchange(self.ast)

        golang_code = ["\n"]

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]

                    golang_code.append(
                        "func (actor *{}Actor) Assign{}Callback(callback {}{}Callback) {{\n".format(
                            exchangeName, function_name, exchangeName, function_name)
                    )
                    golang_code.append(
                        "\tactor.{}{}Callback = callback\n".format(exchangeName[0].lower() + exchangeName[1:],
                                                                   function_name))
                    golang_code.append("}\n\n")

        return "".join(golang_code)

    # generates the entire actor
    def generate(self):
        code = ["// Actor Section\n", self.__generate_actor_struct(),
                self.__generate_actor_constructor(), self.__generate_init(), self.__generate_funcs()]

        return "".join(code)
