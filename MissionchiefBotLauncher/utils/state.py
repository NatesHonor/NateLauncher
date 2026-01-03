process_cache = {}

def add_process(name, process):
    process_cache[name] = {
        "pid": process.pid,
        "state": "running",
        "process": process
    }

def stop_all():
    for name, entry in process_cache.items():
        proc = entry["process"]
        if proc and entry["state"] == "running":
            try:
                proc.kill()
                entry["state"] = "stopped"
            except Exception:
                entry["state"] = "error"

def get_process_info(name):
    return process_cache.get(name)

def list_processes():
    return {
        name: {"pid": entry["pid"], "state": entry["state"]}
        for name, entry in process_cache.items()
    }
