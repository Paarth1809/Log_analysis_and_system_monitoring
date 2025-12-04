def run_matching(payload=None):
    from matching_engine.matcher import main as matcher_main
    return matcher_main(payload)
