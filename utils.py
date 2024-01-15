from models.AST import Program
import json

def ast_to_json(program: Program) -> dict:
    """ Converts the AST into a human readable JSON """
    output: dict = {
        program.type(): program.json()
    }

    # print(output)
    with open("./debug/test-ast.json", "w") as f:
        json.dump(output, f, indent=3)
