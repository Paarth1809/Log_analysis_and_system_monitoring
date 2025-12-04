# parser_engine/__init__.py
# Wrap existing script execution inside a callable function.
import sys
import io
from backend.services.runner_service import log_message

def run_parser(payload=None, task_id=None):
    from parser_engine.parser import main as parser_main
    from parser_engine.insert_to_mongo import main as insert_main
    
    # Custom print function to capture output
    original_print = print
    
    def custom_print(*args, **kwargs):
        # Construct message
        sep = kwargs.get('sep', ' ')
        msg = sep.join(map(str, args))
        
        # Log to task if task_id is present
        if task_id:
            log_message(task_id, msg)
            
        # Also print to original stdout for debugging
        original_print(*args, **kwargs)
        
    # Monkey patch print
    import builtins
    builtins.print = custom_print
    
    try:
        # Run parser
        if task_id: log_message(task_id, "Starting parser...")
        parse_res = parser_main(payload)
        
        # Run insertion
        if task_id: log_message(task_id, "Starting database insertion...")
        insert_res = insert_main(payload)
        
        return {"parser": parse_res, "insert": insert_res}
    finally:
        # Restore print
        builtins.print = original_print
