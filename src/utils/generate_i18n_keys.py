import json
from pathlib import Path


def generate_enum(json_path: Path, output_path: Path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = ["from enum import Enum\n\n", "class I18NKey(str, Enum):\n"]

    for section, items in data.items():
        for key in items.keys():
            full_key = f"{section}.{key}"
            enum_name = f"{section.upper()}_{key}"
            lines.append(f"    {enum_name} = '{full_key}'\n")

    output_path.write_text("".join(lines), encoding="utf-8")
    print(f"✅ i18n keys written to {output_path}")


if __name__ == "__main__":
    json_path = Path("../i18n/i18n.json")
    output_path = Path("../i18n/i18n_keys.py")
    generate_enum(json_path, output_path)
