def generate(ast):
    dto = []

    for node in ast.children:
        if node.data == 'type_def':
            for type in node.children[0].children:
                struct_name = type.children[0]
                dto.append("type {} struct {{\n".format(struct_name))
                fields = []

                for params in type.children[1].children:
                    field_name = params.children[0]
                    field_type = params.children[1]

                    if field_type.lower() == 'string':
                        field_type = 'string'
                    elif field_type.lower() == 'int':
                        field_type = 'int'
                    elif field_type.lower() == 'bool':
                        field_type = 'bool'

                    fields.append((field_name, field_type))
                    dto.append("\t{} {} `json:\"{}\"`\n".format(field_name, field_type, field_name))

                dto.append("}\n\n")

                for field_name, field_type in fields:
                    # Generate Getter
                    getter_name = 'Get' + field_name.capitalize()
                    dto.append("func (x *{}) {}() {} {{\n".format(struct_name, getter_name, field_type))
                    dto.append("\treturn x.{}\n".format(field_name))
                    dto.append("}\n\n")
                    # Generate Setter
                    setter_name = 'Set' + field_name.capitalize()
                    dto.append("func (x *{}) {}(val {}) *{} {{\n".format(struct_name, setter_name, field_type, struct_name))
                    dto.append("\tx.{} = val\n".format(field_name))
                    dto.append("\treturn x\n")
                    dto.append("}\n\n")

    return "".join(dto)