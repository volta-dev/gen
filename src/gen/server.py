import hcl2
from src.gen.shared import get_exchange


class Server:
    def __init__(self, input_string):
        self.ast = hcl2.load(input_string)

    # generates the struct for the server
    def __generate_server_struct(self):
        # Extract the exchange name from the abstract syntax tree (AST)
        exchange_name = get_exchange(self.ast)

        # This list will hold lines of generated Go code
        golang_code = []

        # Start the struct declaration
        golang_code.append(f"type {exchange_name}Server struct {{\n")
        golang_code.append("\tbroker *volta.App\n\n")

        # Loop through child nodes in AST
        for node in self.ast.children:
            if node.data == 'action_def':
                # For every action in the action definition, add a line to the struct
                for action in node.children[0].children:
                    function_name = action.children[0]
                    # Format the callback structure
                    callback_format = f"\t{exchange_name[0].lower() + exchange_name[1:]}{function_name}" + \
                                      f"Callback {exchange_name}{function_name}Callback\n"
                    golang_code.append(callback_format)

        # End the struct declaration
        golang_code.append("}\n\n")

        # Joining all the Go code lines into a single string
        return "".join(golang_code)

    # generates the constructor for the server
    def __generate_server_constructor(self):
        # Extract the exchange name from the abstract syntax tree (AST)
        exchange = get_exchange(self.ast)

        # Use f-string to interpolate variables into the string template
        constructor = f"func New{exchange}Server(broker *volta.App) *{exchange}Server {{\n"
        constructor += f"\treturn &{exchange}Server{{broker: broker}}\n}}\n\n"

        return constructor

    # generate the init function for exchange and queues
    def __generate_init(self):
        # Get the exchange name from the AST.
        exchange_name = get_exchange(self.ast)

        # Initialize golang_code with the function signature.
        golang_code = [
            f"func (server *{exchange_name}Server) Init() {{\n",
            f"\tserver.broker.AddExchanges(volta.Exchange{{Name: \"{exchange_name[0].lower() + exchange_name[1:]}\", Type: \"topic\"}})\n\n"
        ]

        # Scan the AST children.
        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    routing_key = action.children[3][1]
                    golang_code.append(
                        f"\tserver.broker.AddQueue(volta.Queue{{Name: {routing_key}, RoutingKey: {routing_key}, "
                        f"Exchange: \"{exchange_name[0].lower() + exchange_name[1:]}\"}})\n"
                    )

        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    routing_key = action.children[3][1]
                    func_name = action.children[0]
                    type_name = action.children[1][:1].lower() + action.children[1][1:]
                    func_arg = action.children[1] if action.children[1] is not None else ""
                    return_arg = action.children[2] if action.children[2] is not None else ""

                    # Format and add the server callback.
                    exchange_name_lower = exchange_name[0].lower() + exchange_name[1:]
                    golang_code.append(f"\n\tserver.broker.AddConsumer({routing_key}, func (ctx *volta.Ctx) error {{\n")

                    # Different scenarios for generating specific parts of callback method
                    # Uses f-strings to make string formatting clearer
                    if func_arg == "" and return_arg == "":
                        golang_code.append(f"\t\tserver.{exchange_name_lower}{func_name}Callback()\n"
                                           "\t\treturn ctx.Ack(false)\n"
                                           "\t}})\n")
                    elif func_arg == "" and return_arg != "":
                        golang_code.append(
                            f"\t\treturn ctx.ReplyJSON(server.{exchange_name_lower}{func_name}Callback())\n"
                            "\t}})\n")
                    elif func_arg != "" and return_arg == "":
                        golang_code.append(f"\t\tvar data {func_arg}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           f"\t\tserver.{exchange_name_lower}{func_name}Callback(data)\n"
                                           "\t\treturn ctx.Ack(false)\n"
                                           "\t}})\n")
                    elif func_arg != "" and return_arg != "":
                        golang_code.append(f"\t\tvar data {func_arg}\n"
                                           "\t\tif err := ctx.BindJSON(&data); err != nil {{\n"
                                           "\t\t\treturn err\n"
                                           "\t\t}}\n"
                                           f"\t\treturn ctx.ReplyJSON(server.{exchange_name_lower}{func_name}Callback(data))\n"
                                           "\t}})\n")

        # Append the closing bracket to the golang_code.
        golang_code.append("}\n\n")

        # Join all elements of the golang_code into a single string and return.
        return "".join(golang_code)

    # generates the functions for the server
    def __generate_funcs(self):
        # Extract the exchange name from the AST
        exchange_name = get_exchange(self.ast)

        # Prepare for golang_code
        golang_code = ["\n"]

        # Iterating over child nodes in AST
        for node in self.ast.children:

            # Check if the child is an action definition
            if node.data == 'action_def':

                # Iterating over all actions for this node
                for action in node.children[0].children:
                    function_name = action.children[0]

                    # Generate the function signature
                    func_signature = f"func (server *{exchange_name}Server) Assign{function_name}"
                    func_signature += f"Callback(callback {exchange_name}{function_name}Callback) {{\n"
                    golang_code.append(func_signature)

                    # Generate the callback assignment
                    assignment = f"\tserver.{exchange_name[0].lower() + exchange_name[1:]}{function_name}Callback = callback\n"
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
