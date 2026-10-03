import json
import re
import sys
from datetime import datetime
from pathlib import Path

import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel


DB_FILE = Path(__file__).parent / "db.json"

console = Console()


STEPS = [
    ("drops", "Drop"),
    ("categories", "Categoría"),
    ("subcategories", "Subcategoría"),
    ("base_colors", "Color base"),
    ("designs", "Diseño"),
    ("design_colors", "Color del diseño"),
    ("sizes", "Talla"),
]


def clear_screen():
    """
    Limpia completamente la terminal.
    ANSI funciona en macOS/Linux y terminales modernas.
    """
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def load_db():
    return json.loads(
        DB_FILE.read_text(encoding="utf-8")
    )


def save_db(db):
    DB_FILE.write_text(
        json.dumps(
            db,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def normalize_code(value):
    value = value.strip().upper()
    value = re.sub(r"[\s_/]+", "-", value)
    value = re.sub(r"[^A-Z0-9-]", "", value)
    value = re.sub(r"-+", "-", value)

    return value.strip("-")


def validate_code(value):
    code = normalize_code(value)

    if not code:
        return "El valor no puede estar vacío."

    if not re.fullmatch(
        r"[A-Z0-9]+(?:-[A-Z0-9]+)*",
        code,
    ):
        return "Solo se permiten letras, números y guiones."

    if len(code) > 20:
        return "El código no puede tener más de 20 caracteres."

    return True


def build_sku(db, values):
    return "-".join(
        [
            db["config"]["brand"]["code"],
            *values,
        ]
    )


def render_screen(db, values, step):
    """
    Renderiza una pantalla completamente nueva.
    """
    clear_screen()

    sku = build_sku(db, values)

    console.print(
        Panel(
            f"[bold white]GF[/bold white] "
            f"[dim]·[/dim] "
            f"[cyan]SKU GENERATOR[/cyan]\n\n"
            f"[dim]SKU actual[/dim]\n"
            f"[bold cyan]{sku}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    console.print(
        f"[dim]Step {step}/{len(STEPS)}[/dim]"
    )

    console.print()


def create_new_option(db, key, label):
    value = questionary.text(
        f"Nuevo {label.lower()}",
        instruction=(
            "Se convertirá automáticamente "
            "a formato SKU"
        ),
    ).ask()

    if value is None:
        return None

    code = normalize_code(value)

    error = validate_code(code)

    if error is not True:
        console.print(
            f"\n[yellow]⚠ {error}[/yellow]"
        )

        questionary.press_any_key_to_continue(
            "Presiona cualquier tecla para continuar..."
        ).ask()

        return create_new_option(
            db,
            key,
            label,
        )

    existing = next(
        (
            item
            for item in db.get(key, [])
            if item["code"] == code
        ),
        None,
    )

    if existing:
        return code

    db.setdefault(key, []).append(
        {
            "code": code,
            "name": value.strip(),
        }
    )

    save_db(db)

    return code


def choose_option(db, key, label):
    options = db.get(key, [])

    choices = [
        Choice(
            title=(
                f"{item['code']} · "
                f"{item['name']}"
            ),
            value=item["code"],
        )
        for item in options
    ]

    choices.append(
        Choice(
            title="＋ Crear nuevo",
            value="__new__",
        )
    )

    answer = questionary.select(
        label,
        choices=choices,
        instruction=(
            "↑↓ navegar · Enter seleccionar"
        ),
    ).ask()

    if answer is None:
        return None

    if answer == "__new__":
        return create_new_option(
            db,
            key,
            label,
        )

    return answer


def sku_exists(db, sku):
    return any(
        product["sku"] == sku
        for product in db.get("products", [])
    )


def create_product(db):
    values = []

    for step, (key, label) in enumerate(
        STEPS,
        start=1,
    ):
        # --------------------------------------------------
        # NUEVO STEP = NUEVA PANTALLA
        # --------------------------------------------------
        render_screen(
            db,
            values,
            step,
        )

        value = choose_option(
            db,
            key,
            label,
        )

        if value is None:
            clear_screen()

            console.print(
                "[yellow]Cancelado.[/yellow]"
            )

            return

        values.append(value)

        # --------------------------------------------------
        # AQUÍ limpiamos inmediatamente después del prompt.
        # El siguiente loop volverá a renderizar la pantalla.
        # --------------------------------------------------
        clear_screen()

    # ------------------------------------------------------
    # Pantalla final
    # ------------------------------------------------------
    render_screen(
        db,
        values,
        len(STEPS),
    )

    sku = build_sku(
        db,
        values,
    )

    console.print(
        Panel(
            f"[bold cyan]{sku}[/bold cyan]",
            title="SKU final",
            border_style="green",
            padding=(1, 2),
        )
    )

    if sku_exists(db, sku):
        console.print(
            "\n[yellow]⚠ Este SKU ya existe.[/yellow]"
        )
        return

    console.print()

    save = questionary.confirm(
        "¿Guardar este SKU?",
        default=True,
    ).ask()

    if not save:
        clear_screen()

        console.print(
            "[yellow]Cancelado.[/yellow]"
        )

        return

    product = {
        "sku": sku,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
    }

    for (key, _), value in zip(
        STEPS,
        values,
    ):
        product[key] = value

    db.setdefault(
        "products",
        [],
    ).append(product)

    save_db(db)

    clear_screen()

    console.print(
        Panel(
            f"[bold green]✓ SKU guardado[/bold green]\n\n"
            f"[bold cyan]{sku}[/bold cyan]",
            border_style="green",
            padding=(1, 2),
        )
    )


def main():
    try:
        db = load_db()
        create_product(db)

    except KeyboardInterrupt:
        clear_screen()

        console.print(
            "[yellow]Cancelado.[/yellow]"
        )


if __name__ == "__main__":
    main()
