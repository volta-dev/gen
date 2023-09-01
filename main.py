import gen.actor
import gen.dto
import gen.typer as typer

test_input = '''
exchange = "user"

types {
    CreateUser {
        name string
        email int
        password bool
    }
    ReturnUser {
        id int
    }
}

actions {
    Register(CreateUser) ReturnUser @routingKey("user.register")
    Fetch1(ReturnUser) @routingKey("user.test")
}
'''


dto = gen.dto.Dto(test_input)
gen = gen.actor.Actor(test_input)
typ = typer.Typer(test_input)

# write to file
with open('exchange_gen.go', 'w') as f:
    f.write(dto.generate())
    f.write(typ.generate())
    f.write(gen.generate())
