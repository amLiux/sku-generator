from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import (
    Footer,
    Header,
    Label,
    Select,
    Static,
    Input,
    Button,
)

from .database import Database
from .validation import normalize_and_validate


FIELDS = [
    ("drop", "Drop"),
    ("categories", "Category"),
    ("subcategories", "Subcategory"),
    ("base_colors", "Base Color"),
    ("designs", "Design"),
    ("design_colors", "Design Color"),
    ("sizes", "Size"),
]


class SKUApp(App):
    CSS = """
    Screen {
        background: $surface;
    }

    #main {
        width: 80;
        height: auto;
        margin: 2 4;
        padding: 2 4;
        border: round $primary;
    }

    #title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .step {
        margin-bottom: 2;
    }

    .step-title {
        text-style: bold;
        margin-bottom: 1;
    }

    .hint {
        color: $text-muted;
    }

    Select {
        width: 100%;
    }

    Input {
        width: 100%;
    }

    #preview {
        margin-top: 2;
        padding: 2;
        border: round $success;
        color: $success;
    }

    #actions {
        margin-top: 2;
        height: auto;
    }

    Button {
        margin-right: 1;
    }

    #message {
        margin-top: 1;
        color: $warning;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "reset", "Reset"),
    ]

    def __init__(self):
        super().__init__()

        self.db = Database()

        self.values: dict[str, str] = {}

        self.current_index = 0

        self.pending_field: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="main"):
            yield Label(
                "GF SKU GENERATOR",
                id="title",
            )

            yield Static(
                "Create a product SKU step by step.",
                classes="hint",
            )

            yield Container(id="content")

            yield Static("", id="preview")

            yield Static("", id="message")

            with Container(id="actions"):
                yield Button(
                    "Back",
                    id="back",
                    variant="default",
                )

                yield Button(
                    "Next",
                    id="next",
                    variant="primary",
                )

                yield Button(
                    "Save SKU",
                    id="save",
                    variant="success",
                    disabled=True,
                )

                yield Button(
                    "Reset",
                    id="reset",
                    variant="warning",
                )

        yield Footer()

    def on_mount(self) -> None:
        self.show_current_step()

    def show_current_step(self) -> None:
        content = self.query_one("#content", Container)
        content.remove_children()

        self.pending_field = None

        field, label = FIELDS[self.current_index]

        options = self.db.get_options(field)

        option_items = [
            (f"{option['code']} — {option['name']}", option["code"])
            for option in options
        ]

        option_items.append(
            ("+ Add new", "__NEW__")
        )

        content.mount(
            Label(
                f"{self.current_index + 1}. {label}",
                classes="step-title",
            )
        )

        select = Select(
            option_items,
            prompt=f"Select {label}",
            id="selector",
        )

        content.mount(select)

        self.update_buttons()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "selector":
            return

        value = event.value

        if value == "__NEW__":
            self.show_new_value_input()
            return

        if value is None:
            return

        field, _ = FIELDS[self.current_index]

        self.values[field] = str(value)

        self.clear_message()

        self.refresh_preview()

    def show_new_value_input(self) -> None:
        content = self.query_one("#content", Container)

        content.remove_children()

        field, label = FIELDS[self.current_index]

        content.mount(
            Label(
                f"New {label}",
                classes="step-title",
            )
        )

        content.mount(
            Static(
                "Enter a name or code. It will be normalized "
                "to a SKU-safe value.",
                classes="hint",
            )
        )

        content.mount(
            Input(
                placeholder="e.g. Dark Blue",
                id="new-value",
            )
        )

        content.mount(
            Button(
                "Add",
                id="add-value",
                variant="primary",
            )
        )

        self.pending_field = field

    def on_button_pressed(
        self,
        event: Button.Pressed,
    ) -> None:
        button_id = event.button.id

        if button_id == "next":
            self.next_step()

        elif button_id == "back":
            self.previous_step()

        elif button_id == "save":
            self.save_product()

        elif button_id == "reset":
            self.action_reset()

        elif button_id == "add-value":
            self.add_new_value()

    def add_new_value(self) -> None:
        if not self.pending_field:
            return

        input_widget = self.query_one("#new-value", Input)

        raw_value = input_widget.value

        normalized, error = normalize_and_validate(raw_value)

        if error:
            self.show_message(error)
            return

        assert normalized is not None

        field = self.pending_field

        existing = self.db.find_option(
            field,
            normalized,
        )

        if existing:
            self.values[field] = normalized
            self.show_message(
                f"Using existing value: {normalized}"
            )
            self.refresh_preview()
            return

        self.db.add_option(
            field,
            code=normalized,
            name=raw_value.strip(),
        )

        self.values[field] = normalized

        self.show_message(
            f"Added {normalized} to the catalog."
        )

        self.refresh_preview()

    def next_step(self) -> None:
        field, label = FIELDS[self.current_index]

        if field not in self.values:
            self.show_message(
                f"Please select or add a {label.lower()}."
            )
            return

        if self.current_index >= len(FIELDS) - 1:
            self.show_message(
                "All fields completed. Review the SKU below."
            )
            return

        self.current_index += 1
        self.show_current_step()

    def previous_step(self) -> None:
        if self.current_index == 0:
            return

        self.current_index -= 1
        self.show_current_step()

    def build_sku(self) -> str:
        parts = [
            self.db.brand_code,
            self.values.get("drop", ""),
            self.values.get("categories", ""),
            self.values.get("subcategories", ""),
            self.values.get("base_colors", ""),
            self.values.get("designs", ""),
            self.values.get("design_colors", ""),
            self.values.get("sizes", ""),
        ]

        return self.db.separator.join(parts)

    def refresh_preview(self) -> None:
        preview = self.query_one("#preview", Static)

        sku = self.build_sku()

        if any(
            not self.values.get(field)
            for field, _ in FIELDS
        ):
            preview.update(
                f"SKU Preview\n\n{sku}"
            )
            self.query_one("#save", Button).disabled = True
            return

        if self.db.sku_exists(sku):
            preview.update(
                f"SKU Preview\n\n"
                f"{sku}\n\n"
                f"⚠ SKU already exists."
            )
            self.query_one("#save", Button).disabled = True
            return

        preview.update(
            f"SKU Preview\n\n{sku}\n\n"
            f"✓ SKU is available."
        )

        self.query_one("#save", Button).disabled = False

    def save_product(self) -> None:
        sku = self.build_sku()

        if self.db.sku_exists(sku):
            self.show_message(
                f"SKU already exists: {sku}"
            )
            return

        product = {
            "sku": sku,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "brand": self.db.brand_code,
            "drop": self.values["drop"],
            "category": self.values["categories"],
            "subcategory": self.values["subcategories"],
            "base_color": self.values["base_colors"],
            "design": self.values["designs"],
            "design_color": self.values["design_colors"],
            "size": self.values["sizes"],
        }

        self.db.add_product(product)

        self.show_message(
            f"✓ Saved {sku}"
        )

        self.action_reset()

    def show_message(self, message: str) -> None:
        self.query_one("#message", Static).update(message)

    def clear_message(self) -> None:
        self.query_one("#message", Static).update("")

    def update_buttons(self) -> None:
        self.query_one("#back", Button).disabled = (
            self.current_index == 0
        )

        is_last = self.current_index == len(FIELDS) - 1

        self.query_one("#next", Button).disabled = is_last

        self.refresh_preview()

    def action_reset(self) -> None:
        self.values = {}
        self.current_index = 0
        self.pending_field = None

        self.clear_message()
        self.show_current_step()


def main() -> None:
    app = SKUApp()
    app.run()


if __name__ == "__main__":
    main()
