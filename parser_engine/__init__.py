# parser_engine/__init__.py
# Wrap existing script execution inside a callable function.

def run_parser(payload=None):
    """
    Use this function to call your existing parser script's main logic.
    Keep it short and import the code from parser_engine.parser
    """
    from parser_engine.parser import main as parser_main
    # parser_main should be a function that accepts optional payload dict
    return parser_main(payload)
