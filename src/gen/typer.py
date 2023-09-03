import hcl2


class Typer:
    def __init__(self, input_string):
        self.data = hcl2.loads(input_string)

    # generate constants for the actor
    def __generate_constants(self):
        # Extract the exchange name from the abstract syntax tree
        exchange_name = self.data['exchange']

        # Start with a comment in the code
        golang_code = ["\n// Constants Section\n"]

        # Create a constant for the exchange name
        lower_exchange_name = exchange_name.lower()
        golang_code.append(f"const {lower_exchange_name}Exchange = \"{lower_exchange_name}\"\n")

        # Iterate over the actions defined
        for action in self.data['actions']:
            for name in action:
                golang_code.append(f"const {lower_exchange_name}{name} = \"{action[name]['routing']}\"\n")

        # Join the generated lines of code into a single string and return
        return "".join(golang_code)

    # generate callback type for the actor
    def __generate_callback_type(self):
        # Extract the exchange name
        exchange_name = self.data['exchange']

        # Begin golang_code's array with a comment to indicate where the Callback Type Section begins
        golang_code = ["\n// Callback Type Section\n"]

        # Traverse through the actions
        for action in self.data['actions']:
            for name in action:
                # Get 'action_arg' if they exist, else leave as empty string
                action_arg = "" if action[name]['input'] is None else f"data {action[name]['input']}"

                # Generate function definition and append to the golang_code list
                callback_type = f"type {exchange_name}{name}Callback func({action_arg}) {action[name]['output']}\n"
                golang_code.append(callback_type)

        golang_code.append("\n")

        # Return golang_code list as a single string
        return "".join(golang_code)

    # generate generates the entire types
    def generate(self):
        code = [self.__generate_constants(), self.__generate_callback_type()]
        return "".join(code)