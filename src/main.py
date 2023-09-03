import src.gen.server as actor
import src.gen.dto as dto
import src.gen.typer as typer
import argparse
import hcl2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="volta.hcl")
    parser.add_argument("-o", "--output", default="output.go")
    args = parser.parse_args()

    # read file from flag
    with open(args.file, 'r') as f:
        dtogen = dto.Dto(f)
        # actorgen = actor.Server(data)
        # typergen = typer.Typer(data)
        #
        # write to file
        with open(args.output, 'w') as f:
              f.write(dtogen.generate())
        #     f.write(typergen.generate())
        #     f.write(actorgen.generate())


if __name__ == "__main__":
    main()
