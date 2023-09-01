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
    Fetch1() ReturnUser @routingKey("user.test")
}
'''


generator = gen.gen.Gen(test_input)

# write to file
with open('exchange_gen.go', 'w') as f:
    f.write(generator.generate())
