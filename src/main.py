import src.gen.server as actor
import src.gen.dto as dto
import src.gen.typer as typer

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


def main():
    dtogen = dto.Dto(test_input)
    actorgen = actor.Server(test_input)
    typergen = typer.Typer(test_input)

    # write to file
    with open('exchange_gen.go', 'w') as f:
        f.write(dtogen.generate())
        f.write(typergen.generate())
        f.write(actorgen.generate())
