from parser.parser import parser
from gen.shared import get_exchange


class Typer:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # generate constants for the actor
    def __generate_constants(self):
        # Extract the exchange name from the abstract syntax tree
        exchange_name = get_exchange(self.ast)

        # Start with a comment in the code
        golang_code = ["\n// Constants Section\n"]

        # Create a constant for the exchange name
        lower_exchange_name = exchange_name.lower()
        golang_code.append(f"const {lower_exchange_name}Exchange = \"{lower_exchange_name}\"\n")

        # Iterate over the actions defined in the AST
        for node in self.ast.children:
            if node.data == 'action_def':
                for action in node.children[0].children:
                    function_name = action.children[0]
                    routing_key = action.children[3][1]

                    # For each action, create a constant for the routing key
                    golang_code.append(f"const {lower_exchange_name}{function_name} = {routing_key}\n")

        # Join the generated lines of code into a single string and return
        return "".join(golang_code)

    # generate callback type for the actor
    def __generate_callback_type(self):
        # Extract the exchange name from the AST
        exchange_name = get_exchange(self.ast)

        # Begin golang_code's array with a comment to indicate where the Callback Type Section begins
        golang_code = ["\n// Callback Type Section\n"]

        # Traverse through child nodes in the AST
        for node in self.ast.children:
            if node.data == 'action_def':
                # Within each 'action_def' node, traverse its children
                for action in node.children[0].children:
                    function_name = action.children[0]

                    # Get 'action_arg' and 'return_arg' if they exist, else leave as empty string
                    action_arg = "" if action.children[1] is None else f"data {action.children[1]}"
                    return_arg = "" if action.children[2] is None else action.children[2]

                    # Generate function definition and append to the golang_code list
                    callback_type = f"type {exchange_name}{function_name}Callback func({action_arg}) {return_arg}\n"
                    golang_code.append(callback_type)

        golang_code.append("\n")

        # Return golang_code list as a single string
        return "".join(golang_code)

    # generate generates the entire types
    def generate(self):
        code = [self.__generate_constants(), self.__generate_callback_type()]
        return "".join(code)