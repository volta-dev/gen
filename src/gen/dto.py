import hcl2


class Dto:
    def __init__(self, input_string):
        self.data = hcl2.loads(input_string)

    def _generate_struct(self, struct_name, fields):
        # Formats struct field depends on internal type
        field_format = "\t{} {} `json:\"{},omitempty\"`\n"

        fields_str = []
        for field in fields:
            field_type = fields[field][0]
            fields_str.append(field_format.format(field.capitalize(), field_type, field.lower()))

        # f-string is used for better readability
        return [f"type {struct_name} struct {{\n", *fields_str, "}\n"]

    def _generate_getters_and_setters(self, struct_name, fields):
        funcs = []
        for field in fields:
            field_type = fields[field][0]

            # f-string is used for better readability
            getter = (f"\nfunc (s *{struct_name}) Get{field.capitalize()}() {field_type} {{\n"
                      f"\treturn s.{field}\n"
                      f"}}\n")
            setter = (f"\nfunc (s *{struct_name}) Set{field.capitalize()}(value {field_type}) {{\n"
                      f"\ts.{field} = value\n"
                      f"}}\n")

            funcs.append(getter)
            funcs.append(setter)

        funcs.append("\n")

        return funcs

    def generate(self):
        dto = ["// DTO Section\n"]

        for types in self.data['types']:
            for typeNames in types:
                dto += self._generate_struct(typeNames, types[typeNames])
                dto += self._generate_getters_and_setters(typeNames, types[typeNames])

        return "".join(dto)