import hcl2

from src.gen.validator import golang_types


class Client:
    def __init__(self, input_string):
        self.data = hcl2.loads(input_string)

    # generates the struct for the server
    def __generate_client_struct(self):
        exchange_name = self.data['exchange']

        # This list will hold lines of generated Go code
        golang_code = [
            f"type {exchange_name.capitalize()}Client struct {{\n",
            "\tbroker *volta.App\n",
            "}\n\n"
        ]

        # Joining all the Go code lines into a single string
        return "".join(golang_code)

    # generates the constructor for the server
    def __generate_client_constructor(self):
        exchange_name = self.data['exchange']

        # Use f-string to interpolate variables into the string template
        constructor = [
            f"func New{exchange_name.capitalize()}Client(broker *volta.App) *{exchange_name.capitalize()}Client {{\n",
            f"\treturn &{exchange_name.capitalize()}Client{{broker: broker}}\n}}\n"
        ]

        return "".join(constructor)

    # generates the functions for the server
    def __generate_funcs(self):
        exchange_name = self.data['exchange']

        # Prepare for golang_code
        golang_code = ["\n"]

        # Iterating over child nodes in AST
        for action in self.data['actions']:
            for name in action:
                action_arg = "" if action[name]['input'] is None else f"data {action[name]['input']}"
                action_ret = "error" if action[name]['output'] == "" else f"(*{action[name]['output']}, error)"

                # Generate the function signature
                func_signature = f"func (client *{exchange_name.capitalize()}Client) {name}"
                func_signature += f"({action_arg}) {action_ret} {{\n"
                golang_code.append(func_signature)

                # Generate the callback assignment
                assignment = f"\t"
                if action[name]['output'] != "":
                    if action[name]['output'] not in golang_types:
                        assignment += f"result := &{action[name]['output']}{{}}\n"
                    else:
                        assignment += f"var result {action[name]['output']}\n"
                    assignment += f"\tif err := client.broker.RequestJSON({exchange_name.capitalize()}{name}, {exchange_name.capitalize()}Exchange, data, &result); err != nil{{\n"
                    assignment += f"\t\treturn nil, err\n\t}}\n"
                    assignment += f"\treturn result, nil\n}}\n\n"
                else:
                    assignment += f"return client.broker.PublishJSON({exchange_name.capitalize()}{name}, data)\n}}\n\n"

                golang_code.append(assignment)

        # Combine to form final golang code
        return "".join(golang_code)

    # generates the entire server
    def generate(self):
        code = [
            "// Client Section\n",
            self.__generate_client_struct(),
            self.__generate_client_constructor(),
            self.__generate_funcs()
        ]

        return "".join(code)
