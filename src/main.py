import src.gen.server as server
import src.gen.client as client
import src.gen.dto as dto
import src.gen.typer as typer
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="volta.volta")
    parser.add_argument("-o", "--output", default="output.go")
    args = parser.parse_args()

    # read file from flag
    with open(args.file, 'r') as f:
        data = f.read()

    dtogen = dto.Dto(data)
    typergen = typer.Typer(data)
    servergen = server.Server(data)
    clientgen = client.Client(data)

    # write to file
    with open(args.output, 'w') as f:
        f.write(dtogen.generate())
        f.write(typergen.generate())
        f.write(servergen.generate())
        f.write(clientgen.generate())


if __name__ == "__main__":
    main()
