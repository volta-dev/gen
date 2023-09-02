import src.gen.server as actor
import src.gen.dto as dto
import src.gen.typer as typer
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="File ", default="volta.volta")
    parser.add_argument("-o", "--output", help="User name")
    args = parser.parse_args()

    # read file from flag
    file_data = ''
    with open(args.file, 'r') as f:
        file_data = f.read()

        dtogen = dto.Dto(file_data)
        actorgen = actor.Server(file_data)
        typergen = typer.Typer(file_data)

        # write to file
        with open(args.output, 'w') as f:
            f.write(dtogen.generate())
            f.write(typergen.generate())
            f.write(actorgen.generate())


if __name__ == "__main__":
    main()
