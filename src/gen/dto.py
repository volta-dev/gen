import hcl2


class Dto:
    def __init__(self, input_string):
        self.data = hcl2.load(input_string)

    def _generate_struct(self, struct_name, fields):
        # Formats struct field depends on internal type
        field_format = "\t{} {} `json:\"{},omitempty\"`\n"

        # List comprehensions is used instead of loop to generate fields string.
        fields_str = [field_format.format(field_name.capitalize(), field_type, field_name)
                      for field_name, field_type in fields]

        # f-string is used for better readability
        return [f"type {struct_name} struct {{\n", *fields_str, "}\n"]

    def _generate_getters_and_setters(self, struct_name, fields):
        funcs = []
        for field_name, field_type in fields:
            # f-string is used for better readability
            getter = (f"\nfunc (s *{struct_name}) Get{field_name.capitalize()}() {field_type} {{\n"
                      f"\treturn s.{field_name}\n"
                      f"}}\n")
            setter = (f"\nfunc (s *{struct_name}) Set{field_name.capitalize()}(value {field_type}) {{\n"
                      f"\ts.{field_name} = value\n"
                      f"}}\n")

            funcs.append(getter)
            funcs.append(setter)

        return funcs

    def _generate_mapper_methods(self, struct_name, internal_struct_name, fields):
        # f-string is used for better readability
        to_internal = [f"\nfunc (s *{struct_name}) ToInternal() {internal_struct_name} {{\n\tinternal := {internal_struct_name}{{}}\n"]
        from_internal = [f"func {struct_name[:1].lower() + struct_name[1:]}FromInternal(internal {internal_struct_name}) {struct_name} {{\n\texternal := {struct_name}{{}}\n"]

        for field_name, _ in fields:
            export_field_name = field_name.capitalize()
            to_internal.append(f"\tinternal.{export_field_name} = s.Get{field_name.capitalize()}\n")
            from_internal.append(f"\texternal.Set{field_name.capitalize()}(internal.{export_field_name})\n")

        to_internal.append("\treturn internal\n}\n\n")
        from_internal.append("\treturn external\n}\n\n")

        return to_internal + from_internal

    def generate(self):
        dto = ["// DTO Section\n"]

        for types in self.data['types']:
            for typeNames in types:
                for params in types[typeNames]:
                    dto += self._generate_struct(typeNames, params)
                    dto += self._generate_getters_and_setters(typeNames, params)

        return "".join(dto)