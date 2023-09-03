import hcl2


class Dto:
    def __init__(self, input_string):
        self.data = hcl2.load(input_string)

    def _generate_struct(self, struct_name, fields):
        # Formats struct field depends on internal type
        field_format = "\t{} {} `json:\"{},omitempty\"`\n"

        fields_str = []
        for field in fields:
            fields_str.append(field_format.format(field.capitalize(), fields[field][0], field.lower()))

        # f-string is used for better readability
        return [f"type {struct_name} struct {{\n", *fields_str, "}\n"]

    def _generate_getters_and_setters(self, struct_name, fields):
        funcs = []
        for field in fields:
            # f-string is used for better readability
            getter = (f"\nfunc (s *{struct_name}) Get{field.capitalize()}() {fields[field][0]} {{\n"
                      f"\treturn s.{field}\n"
                      f"}}\n")
            setter = (f"\nfunc (s *{struct_name}) Set{field.capitalize()}(value {fields[field][0]}) {{\n"
                      f"\ts.{field} = value\n"
                      f"}}\n")

            funcs.append(getter)
            funcs.append(setter)

        return funcs

    def generate(self):
        dto = ["// DTO Section\n"]

        for types in self.data['types']:
            for typeNames in types:
                for params in types[typeNames]:
                    dto += self._generate_struct(typeNames, types[typeNames])
                    dto += self._generate_getters_and_setters(typeNames, types[typeNames])

        return "".join(dto)