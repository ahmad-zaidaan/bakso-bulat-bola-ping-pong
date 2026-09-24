from items.item import ItemDefinition


class ItemRegistry:
    """
    Centralized singleton registry for all ingredients and items in the game.
    Allows easy addition, renaming, or modification of items in 1 single place.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.items: dict[str, ItemDefinition] = {}
            cls._instance.aliases: dict[str, str] = {}
            cls._instance._register_default_items()
        return cls._instance

    def _register_default_items(self):
        # 1. Mie Kuning (Yellow Noodles)
        self.register(
            ItemDefinition(
                id="mi_kuning",
                display_name="Mie Kuning",
                sprite_id="mi-kuning",
                price=1000,
                category="noodle",
            )
        )
        self.register_alias("mi-kuning", "mi_kuning")

        # 2. Bihun (Rice Vermicelli)
        self.register(
            ItemDefinition(
                id="mi_bihun",
                display_name="Bihun",
                sprite_id="mi-bihun",
                price=1000,
                category="noodle",
            )
        )
        self.register_alias("mi-bihun", "mi_bihun")

        # 3. Bakso Halus
        self.register(
            ItemDefinition(
                id="bakso_halus",
                display_name="Bakso Halus",
                sprite_id="bakso-halus",
                price=2500,
                category="meatball",
            )
        )
        self.register_alias("bakso-halus", "bakso_halus")
        self.register_alias("bakso", "bakso_halus")

        # 4. Gorengan Panjang
        self.register(
            ItemDefinition(
                id="gorengan_panjang",
                display_name="Gorengan",
                sprite_id="gorengan-panjang",
                price=1000,
                category="topping",
            )
        )
        self.register_alias("gorengan-panjang", "gorengan_panjang")
        self.register_alias("gorengan", "gorengan_panjang")

        # 5. Bakso Urat (optional / fallback)
        self.register(
            ItemDefinition(
                id="bakso_urat",
                display_name="Bakso Urat",
                sprite_id="bakso_urat",
                price=3000,
                category="meatball",
            )
        )
        self.register_alias("bakso-urat", "bakso_urat")

        # 6. Tahu
        self.register(
            ItemDefinition(
                id="tahu",
                display_name="Tahu",
                sprite_id="tahu",
                price=1500,
                category="topping",
            )
        )

        # 7. Kecap
        self.register(
            ItemDefinition(
                id="kecap",
                display_name="Kecap Manis",
                sprite_id="kecap",
                price=500,
                category="sauce",
            )
        )
        self.register_alias("kecap-manis", "kecap")

        # 8. Saos Sambal
        self.register(
            ItemDefinition(
                id="saos_sambal",
                display_name="Saos Sambal",
                sprite_id="saos-sambal",
                price=500,
                category="sauce",
            )
        )
        self.register_alias("saos-sambal", "saos_sambal")
        self.register_alias("sambal", "saos_sambal")

        # 9. Saos Tomat
        self.register(
            ItemDefinition(
                id="saos_tomat",
                display_name="Saos Tomat",
                sprite_id="saos-tomat",
                price=500,
                category="sauce",
            )
        )
        self.register_alias("saos-tomat", "saos_tomat")

        # 10. Bawang Goreng
        self.register(
            ItemDefinition(
                id="bawang_goreng",
                display_name="Bawang Goreng",
                sprite_id="bawang-goreng",
                price=500,
                category="topping",
            )
        )
        self.register_alias("bawang-goreng", "bawang_goreng")

        # 11. Daun Bawang
        self.register(
            ItemDefinition(
                id="daun_bawang",
                display_name="Daun Bawang",
                sprite_id="daun-bawang",
                price=500,
                category="topping",
            )
        )
        self.register_alias("daun-bawang", "daun_bawang")

        # 12. Kuah
        self.register(
            ItemDefinition(
                id="kuah",
                display_name="Kuah",
                sprite_id="kuah",
                price=0,
                category="broth",
            )
        )

    def register(self, item_def: ItemDefinition):
        """Register a new ItemDefinition into the registry."""
        self.items[item_def.id] = item_def

    def register_alias(self, alias_id: str, target_id: str):
        """Map a legacy or shorthand alias (e.g. 'bakso' -> 'bakso_halus')."""
        self.aliases[alias_id] = target_id

    def get(self, item_id: str) -> ItemDefinition | None:
        """Get ItemDefinition by id or alias."""
        resolved_id = self.aliases.get(item_id, item_id)
        return self.items.get(resolved_id)

    def get_price(self, item_id: str) -> int:
        """Get the price of an item."""
        item = self.get(item_id)
        return item.price if item else 0

    def get_all(self) -> list[ItemDefinition]:
        """Returns all registered items."""
        return list(self.items.values())

    def get_by_category(self, category: str) -> list[ItemDefinition]:
        """Returns items matching a given category."""
        return [it for it in self.items.values() if it.category == category]


items_registry = ItemRegistry()
