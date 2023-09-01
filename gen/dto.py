from gen.parser import parser


class Dto:
    def __init__(self, input_string):
        self.ast = parser(input_string)

    # __generate_struct generates a struct with the given name and fields, internal is used to generate the internal dto
    def __generate_struct(self, struct_name, fields, internal=False):
        field_format = "\t{} {} `json:\"{}\"`\n" if not internal else "\t{} {} `json:\"{},omitempty\"`\n"
        fields_str = [field_format.format(field_name.capitalize() if internal else field_name, field_type, field_name)
                      for field_name, field_type in fields]
        return ["type {} struct {{\n".format(struct_name), *fields_str, "}\n"]

    # __generate_getters_and_setters generates the getters and setters for the struct
    def __generate_getters_and_setters(self, struct_name, fields):
        funcs = []
        for field_name, field_type in fields:
            getter = ("\nfunc (s *{}) Get{}() {} {{\n"
                      "\treturn s.{}\n"
                      "}}\n").format(struct_name, field_name.capitalize(), field_type, field_name)
            setter = ("\nfunc (s *{}) Set{}(value {}) {{\n"
                      "\ts.{} = value\n"
                      "}}\n").format(struct_name, field_name.capitalize(), field_type, field_name)
            funcs.append(getter)
            funcs.append(setter)

        funcs.append("\n")

        return funcs

    # __generate_mapper_methods generates the ToInternal and FromInternal methods for the dto
    def __generate_mapper_methods(self, struct_name, internal_struct_name, fields):
        to_internal = ["\nfunc (s *{}) ToInternal() {} {{\n\tinternal := {}{}\n".format(struct_name, internal_struct_name,
                                                                                      internal_struct_name, "{}")]
        from_internal = ["func {}FromInternal(internal {}) {} {{\n\texternal := {}{}\n".format(
            struct_name[:1].lower() + struct_name[1:], internal_struct_name, struct_name, struct_name, "{}")]
        for field_name, _ in fields:
            export_field_name = field_name.capitalize()
            to_internal.append("\tinternal.{} = s.Get{}()\n".format(export_field_name, field_name.capitalize()))
            from_internal.append("\texternal.Set{}(internal.{})\n".format(field_name.capitalize(), export_field_name))
        to_internal.append("\treturn internal\n}\n\n")
        from_internal.append("\treturn external\n}\n\n")
        return to_internal + from_internal

    # __generate_dto generates the entire dto structs
    def generate(self):
        dto = ["// DTO Section\n"]
        for node in self.ast.children:
            if node.data == 'type_def':
                for t in node.children[0].children:
                    struct_name = t.children[0]
                    internal_struct_name = '_internal' + struct_name
                    fields = [(params.children[0], params.children[1]) for params in t.children[1].children]

                    dto += self.__generate_struct(struct_name, fields)
                    dto += self.__generate_getters_and_setters(struct_name, fields)
                    dto += self.__generate_struct(internal_struct_name, fields, internal=True)
                    dto += self.__generate_mapper_methods(struct_name, internal_struct_name, fields)

        return "".join(dto)
