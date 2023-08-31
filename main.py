import gen.dto
import gen.funcs
import parse.main

test_input = '''
exchange = "user"

types {
    CreateUser {
        name string @required
        email int @required
        password bool @required
    }
    ReturnUser {
        id int
        name string
        email int
    }
}

actions {
    Register(CreateUser) ReturnUser @routingKey("user.register")
    Fetch() ReturnUser @routingKey("user.register")
}
'''


ast = parse.main.parser(test_input)
golang_structs_code = gen.dto.generate(ast)
golang_funcs_code = gen.funcs.generate(ast)

print(golang_structs_code)
print(golang_funcs_code)