from app import create_app

app = create_app()

app.json.sort_keys = False

print("========= RUTAS FLASK =========", flush=True)

for rule in app.url_map.iter_rules():
    print(
        f"{rule} -> {sorted(rule.methods)}",
        flush=True
    )

print("===============================", flush=True)

if __name__ == "__main__":
    app.run(host="192.168.100.146", port=5000, debug=True)