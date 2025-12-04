def main(payload=None):
    print("[INFO] Skipping raw log parsing. Using pre-parsed dataset: data/soc_logs.events.json")
    return {"status": "skipped", "reason": "using_preparsed_dataset"}

if __name__ == "__main__":
    main()
