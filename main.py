import json
import re
from pathlib import Path


DB_FILE = Path(__file__).parent / "db.json"


STEPS = [
    ("drops", "Drop"),
    ("categories", "Categoría"),
    ("subcategories", "Subcategoría"),
    ("base_colors", "Color base"),
    ("designs", "Diseño"),
    ("design_colors", "Color del diseño"),
    ("sizes", "Talla"),
]


def load_db():
    return json.loads(DB_FILE.read_text(encoding="utf-8"))


def save_db(db):
    DB_FILE.write_text(
        json.dumps(db, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def normalize(value):
    value = value.strip().upper()
    value = re.sub(r"[\s_/]+", "-", value)
    value = re.sub(r"[^A-Z0-9-]", "", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def valid_code(value):
    return bool(re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+)*", value))


def choose(db, key, label):
    options = db.get(key, [])

    print()
    print(f"? {label}:")

    for index, option in enumerate(options, 1):
        print(f"  {index}) {option['code']} · {option['name']}")

    print(f"  {len(options) + 1}) + Create new")

    while True:
        answer = input("  > ").strip()

        if not answer.isdigit():
            print("  Selecciona una opción válida.")
            continue

        index = int(answer)

        if 1 <= index <= len(options):
            return options[index - 1]["code"]

        if index == len(options) + 1:
            return create_option(db, key, label)

        print("  Selecciona una opción válida.")


def create_option(db, key, label):
    while True:
        value = input(f"\n  Nuevo {label}: ").strip()

        code = normalize(value)

        if not code:
            print("  El valor no puede estar vacío.")
            continue

        if not valid_code(code):
            print("  Solo se permiten A-Z, 0-9 y '-'.")
            continue

        existing = next(
            (
                item
                for item in db.get(key, [])
                if item["code"] == code
            ),
            None,
        )

        if existing:
            print(f"  {code} ya existe. Usando ese valor.")
            return code

        db.setdefault(key, []).append(
            {
                "code": code,
                "name": value,
            }
        )

        save_db(db)

        print(f"  ✓ Agregado: {code}")

        return code


def build_sku(db, values):
    return "-".join(
        [
            db["config"]["brand"]["code"],
            *values,
        ]
    )


def sku_exists(db, sku):
    return any(
        product["sku"] == sku
        for product in db.get("products", [])
    )


def create_product(db):
    print()
    print("GF SKU Generator")
    print("=" * 40)

    values = []

    for key, label in STEPS:
        values.append(
            choose(db, key, label)
        )

    sku = build_sku(db, values)

    print()
    print("=" * 40)
    print(f"SKU: {sku}")
    print("=" * 40)

    if sku_exists(db, sku):
        print("\n⚠ Este SKU ya existe.")
        return

    while True:
        answer = input("\n¿Guardar este SKU? [Y/n] ").strip().lower()

        if answer in ("", "y", "yes", "s", "si"):
            break

        if answer in ("n", "no"):
            print("Cancelado.")
            return

    product = {
        "sku": sku,
        "created_at": __import__("datetime")
        .datetime.now()
        .isoformat(timespec="seconds"),
    }

    for (key, _), value in zip(STEPS, values):
        product[key] = value

    db.setdefault("products", []).append(product)
    save_db(db)

    print(f"\n✓ SKU guardado: {sku}")


def main():
    db = load_db()

    try:
        create_product(db)
    except KeyboardInterrupt:
        print("\n\nCancelado.")


if __name__ == "__main__":
    main()
