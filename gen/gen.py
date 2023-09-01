from gen.parser import parser


class Gen:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # generate dto structs
    def __generate_dto(self):
        dto = ["// DTO Section\n"]

        def generate_struct(struct_name, fields, internal=False):
            field_format = "\t{} {} `json:\"{}\"`\n" if not internal else "\t{} {} `json:\"{},omitempty\"`\n"
            fields_str = [field_format.format(field_name.capitalize() if internal else field_name, field_type, field_name)
                          for field_name, field_type in fields]
            return ["type {} struct {{\n".format(struct_name), *fields_str, "}\n\n"]

        def generate_getters_and_setters(struct_name, fields):
            funcs = []
            for field_name, field_type in fields:
                getter = ("func (s *{}) Get{}() {} {{\n"
                          "\treturn s.{}\n"
                          "}}\n").format(struct_name, field_name.capitalize(), field_type, field_name)
                setter = ("\nfunc (s *{}) Set{}(value {}) {{\n"
                          "\ts.{} = value\n"
                          "}}\n").format(struct_name, field_name.capitalize(), field_type, field_name)
                funcs.append(getter)
                funcs.append(setter)

            funcs.append("\n")

            return funcs

        def generate_mapper_methods(struct_name, internal_struct_name, fields):
            to_internal = ["func (s *{}) ToInternal() {} {{\n\tinternal := {}{}\n".format(struct_name, internal_struct_name, internal_struct_name, "{}")]
            from_internal = ["func {}FromInternal(internal {}) {} {{\n\texternal := {}{}\n".format(struct_name[:1].lower()+struct_name[1:], internal_struct_name, struct_name, struct_name, "{}")]
            for field_name, _ in fields:
                export_field_name = field_name.capitalize()
                to_internal.append("\tinternal.{} = s.Get{}()\n".format(export_field_name, field_name.capitalize()))
                from_internal.append("\texternal.Set{}(internal.{})\n".format(field_name.capitalize(), export_field_name))
            to_internal.append("\treturn internal\n}\n\n")
            from_internal.append("\treturn external\n}\n\n")
            return to_internal + from_internal

        for node in self.ast.children:
            if node.data == 'type_def':
                for t in node.children[0].children:
                    struct_name = t.children[0]
                    internal_struct_name = '_internal' + struct_name
                    fields = [(params.children[0], params.children[1]) for params in t.children[1].children]

                    dto += generate_struct(struct_name, fields)
                    dto += generate_getters_and_setters(struct_name, fields)
                    dto += generate_struct(internal_struct_name, fields, internal=True)
                    dto += generate_mapper_methods(struct_name, internal_struct_name, fields)

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
        exchange_name = self.__get_exchange(self.ast)
        golang_code = ["\ntype {}Actor struct {{\n".format(exchange_name), "\tbroker *volta.App\n\n"]

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
        exchange = self.__get_exchange(self.ast)
        return "func New{}Actor(broker *volta.App) *{}Actor {{\n\treturn &{}Actor{{broker: broker}}\n}}\n\n".format(
            exchange, exchange, exchange)

    # generate constants for the actor
    def __generate_constants(self):
        exchange_name = self.__get_exchange(self.ast)

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


    # generate the init function for exchange and queues
    def __generate_init(self):
        exchange_name = self.__get_exchange(self.ast)

        golang_code = ["func (actor *{}Actor) Init() {{\n".format(exchange_name)]
        golang_code.append("\tactor.broker.AddExchanges(volta.Exchange{{Name: \"{}\", Type: \"topic\"}})\n\n".format(exchange_name[0].lower() + exchange_name[1:]))

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    routing_key = action.children[3][1]
                    golang_code.append(
                        "\tactor.broker.AddQueue(volta.Queue{{Name: {}, RoutingKey: {}, Exchange: \"{}\"}})\n".format(routing_key,
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
                                           "\t}})\n".format(routing_key, exchange_name[0].lower() + exchange_name[1:], action.children[0]))
                    elif func_arg == "" and return_arg != "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\treturn ctx.ReplyJSON(actor.{}{}Callback())\n"
                                           "\t}})\n".format(routing_key, exchange_name[0].lower() + exchange_name[1:], action.children[0]))
                    elif func_arg != "" and return_arg == "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\tvar data _internal{}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           "\t\tactor.{}{}Callback({}FromInternal(data))\n"
                                           "\t\treturn ctx.Ack(false)\n"
                                           "\t}})\n".format(routing_key, action.children[1], exchange_name[0].lower() + exchange_name[1:], action.children[0], action.children[1][:1].lower()+action.children[1][1:]))
                    elif func_arg != "" and return_arg != "":
                        golang_code.append("\n\tactor.broker.AddConsumer({}, func (ctx *volta.Ctx) error {{\n"
                                           "\t\tvar data _internal{}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           "\t\treturn ctx.ReplyJSON(actor.{}{}Callback({}FromInternal(data)))\n"
                                           "\t}})\n".format(routing_key, action.children[1], exchange_name[0].lower() + exchange_name[1:], action.children[0], action.children[1][:1].lower()+action.children[1][1:]))

        golang_code.append("}\n\n")

        return "".join(golang_code)

    # generate callback type for the actor
    def __generate_callback_type(self):
        exchange_name = self.__get_exchange(self.ast)

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

        return "".join(golang_code)

    # generates the functions for the actor
    def __generate_funcs(self):
        exchangeName = self.__get_exchange(self.ast)

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
        code = [self.__generate_dto(), self.__generate_callback_type(), self.__generate_constants(), self.__generate_actor_struct(),
                self.__generate_actor_constructor(), self.__generate_init(), self.__generate_funcs()]

        return "".join(code)
