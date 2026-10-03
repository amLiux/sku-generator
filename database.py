import json
from pathlib import Path
from typing import Any


DEFAULT_DB = {
    "config": {
        "brand": {
            "code": "GF",
            "name": "GF",
        },
        "separator": "-",
    },
    "drops": [],
    "categories": [],
    "subcategories": [],
    "base_colors": [],
    "designs": [],
    "design_colors": [],
    "sizes": [],
    "products": [],
}


class Database:
    def __init__(self, path: str | Path = "db.json"):
        self.path = Path(path)
        self.data: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.data = DEFAULT_DB.copy()
            self.save()
            return

        with self.path.open("r", encoding="utf-8") as file:
            self.data = json.load(file)

    def save(self) -> None:
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")

    def get_options(self, field: str) -> list[dict[str, str]]:
        return self.data.get(field, [])

    def add_option(
        self,
        field: str,
        code: str,
        name: str | None = None,
    ) -> dict[str, str]:
        options = self.data.setdefault(field, [])

        existing = self.find_option(field, code)

        if existing:
            return existing

        option = {
            "code": code,
            "name": name or code,
        }

        options.append(option)
        self.save()

        return option

    def find_option(
        self,
        field: str,
        code: str,
    ) -> dict[str, str] | None:
        for option in self.get_options(field):
            if option["code"] == code:
                return option

        return None

    def sku_exists(self, sku: str) -> bool:
        return any(
            product.get("sku") == sku
            for product in self.data.get("products", [])
        )

    def add_product(self, product: dict[str, Any]) -> None:
        if self.sku_exists(product["sku"]):
            raise ValueError(
                f"SKU already exists: {product['sku']}"
            )

        self.data.setdefault("products", []).append(product)
        self.save()

    @property
    def brand_code(self) -> str:
        return self.data["config"]["brand"]["code"]

    @property
    def separator(self) -> str:
        return self.data["config"].get("separator", "-")
