import hcl2


class Server:
    def __init__(self, input_string):
        self.data = hcl2.loads(input_string)

    # generates the struct for the server
    def __generate_server_struct(self):
        exchange_name = self.data['exchange']

        # This list will hold lines of generated Go code
        golang_code = [
            f"type {exchange_name.capitalize()}Server struct {{\n",
            "\tbroker *volta.App\n\n"
        ]

        # Iterate over the actions defined
        for action in self.data['actions']:
            for name in action:
                golang_code.append(
                    f"\t{exchange_name[0].lower() + exchange_name[1:]}{name}Callback {exchange_name}{name}Callback\n"
                )

        # End the struct declaration
        golang_code.append("}\n\n")

        # Joining all the Go code lines into a single string
        return "".join(golang_code)

    # generates the constructor for the server
    def __generate_server_constructor(self):
        exchange_name = self.data['exchange']

        # Use f-string to interpolate variables into the string template
        constructor = f"func New{exchange_name.capitalize()}Server(broker *volta.App) *{exchange_name.capitalize()}Server {{\n"
        constructor += f"\treturn &{exchange_name.capitalize()}Server{{broker: broker}}\n}}\n\n"

        return constructor

    # generate the init function for exchange and queues
    def __generate_init(self):
        exchange_name = self.data['exchange']

        # Initialize golang_code with the function signature.
        golang_code = [
            f"func (server *{exchange_name.capitalize()}Server) Init() {{\n",
            f"\tserver.broker.AddExchanges(volta.Exchange{{Name: {exchange_name}Exchange, Type: \"topic\"}})\n\n"
        ]

        # generate check is all callbacks assigned
        for action in self.data['actions']:
            for name in action:
                golang_code.append(
                    f"\tif server.{exchange_name}{name}Callback == nil {{\n"
                    f"\t\tlog.Fatal(\"{exchange_name}{name}Callback is not assigned\")\n"
                    f"\t}}\n"
                )

        golang_code.append("\n")

        # Iterate over the actions defined
        for action in self.data['actions']:
            for name in action:
                golang_code.append(
                    f"\tserver.broker.AddQueue(volta.Queue{{Name: {exchange_name}{name}, RoutingKey: {exchange_name}{name}, "
                    f"Exchange: {exchange_name}Exchange}})\n"
                )

        for action in self.data['actions']:
            for name in action:
                func_arg = action[name]['input']
                return_arg = action[name]['output']

                # Format and add the server callback.
                golang_code.append(f"\n\tserver.broker.AddConsumer({exchange_name}{name}, func (ctx *volta.Ctx) error {{\n")

                # Different scenarios for generating specific parts of callback method
                # Uses f-strings to make string formatting clearer
                if func_arg == "" and return_arg == "":
                    golang_code.append(f"\t\tserver.{exchange_name}{name}Callback()\n"
                                       "\t\treturn ctx.Ack(false)\n"
                                       "\t}})\n")
                elif func_arg == "" and return_arg != "":
                    golang_code.append(
                        f"\t\treturn ctx.ReplyJSON(server.{exchange_name}{name}Callback())\n"
                        "\t}})\n")
                elif func_arg != "" and return_arg == "":
                    golang_code.append(f"\t\tvar data {func_arg}\n"
                                       "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                       "\t\t\treturn err\n"
                                       "\t\t}}\n"
                                       f"\t\tserver.{exchange_name}{name}Callback(data)\n"
                                       "\t\treturn ctx.Ack(false)\n"
                                       "\t}})\n")
                elif func_arg != "" and return_arg != "":
                    golang_code.append(f"\t\tvar data {func_arg}\n"
                                       "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                       "\t\t\treturn err\n"
                                       "\t\t}}\n"
                                       f"\t\treturn ctx.ReplyJSON(server.{exchange_name}{name}Callback(data))\n"
                                       "\t}})\n")

        # Append the closing bracket to the golang_code.
        golang_code.append("}\n\n")

        # Join all elements of the golang_code into a single string and return.
        return "".join(golang_code)

    # generates the functions for the server
    def __generate_funcs(self):
        exchange_name = self.data['exchange']

        # Prepare for golang_code
        golang_code = ["\n"]

        # Iterating over child nodes in AST
        for action in self.data['actions']:
            for name in action:
                # Generate the function signature
                func_signature = f"func (server *{exchange_name.capitalize()}Server) Assign{name}"
                func_signature += f"Callback(callback {exchange_name.capitalize()}{name}Callback) {{\n"
                golang_code.append(func_signature)

                # Generate the callback assignment
                assignment = f"\tserver.{exchange_name}{name}Callback = callback\n"
                golang_code.append(assignment)

                # Closing bracket for the function
                golang_code.append("}\n\n")

        # Combine to form final golang code
        return "".join(golang_code)

    # generates the entire server
    def generate(self):
        code = ["// Server Section\n", self.__generate_server_struct(),
                self.__generate_server_constructor(), self.__generate_init(), self.__generate_funcs()]

        return "".join(code)
