import hcl2

golang_types = [
    "string", "int", "int8", "int16", "int32", "int64", "uint", "uint8",
    "uint16", "uint32", "uint64", "uintptr", "byte", "rune", "float32",
    "float64", "complex64", "complex128", "error", "bool", "interface{}",

    "[]string", "[]int", "[]int8", "[]int16", "[]int32", "[]int64", "[]uint",
    "[]uint8", "[]uint16", "[]uint32", "[]uint64", "[]uintptr", "[]byte",
    "[]rune", "[]float32", "[]float64", "[]complex64", "[]complex128",
    "[]error", "[]bool", "[]interface{}"
]


class SchemaValidator:
    def __init__(self, input_string):
        self.data = hcl2.loads(input_string)

    def __exchange_exist(self):
        return 'exchange' in self.data

    def __check_types(self):
        for types in self.data['types']:
            for field in types:
                for params in types[field]:
                    if types[field][params][0] not in golang_types:
                        raise ValueError(f"Type {types[field][params][0]} is not a golang type")

        return True

    def __check_action_type(self):
        isNotError = True

        customTypes = []
        for types in self.data['types']:
            for field in types:
                customTypes.append(field)

        # check for types in actions
        for action in self.data['actions']:
            for field in action:
                if action[field]['input'] not in customTypes and action[field]['input'] not in golang_types:
                    raise ValueError(f"Type {action[field]['input']} is not defined")
                if action[field]['output'] not in customTypes and action[field]['output'] not in golang_types:
                    raise ValueError(f"Type {action[field]['input']} is not defined")

        return isNotError

    def validate(self):
        if not self.__exchange_exist():
            raise ValueError("Exchange is not defined")

        if not self.__check_types():
            return False

        if not self.__check_action_type():
            return False

        return True
