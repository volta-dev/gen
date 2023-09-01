import gen.gen

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


generator = gen.gen.Gen(test_input)

print(generator.generate())