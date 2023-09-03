import src.gen.server as actor
import src.gen.dto as dto
import src.gen.typer as typer
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="volta.hcl")
    parser.add_argument("-o", "--output", default="output.go")
    args = parser.parse_args()

    # read file from flag
    with open(args.file, 'r') as f:
        data = f.read()

    dtogen = dto.Dto(data)
    typergen = typer.Typer(data)
    servergen = actor.Server(data)

    # write to file
    with open(args.output, 'w') as f:
        f.write(dtogen.generate())
        f.write(typergen.generate())
        f.write(servergen.generate())


if __name__ == "__main__":
    main()
