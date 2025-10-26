import os
import re
import json
from pathlib import Path


def extract_strings_from_file(path: Path) -> list[str]:
    pattern = re.compile(
        r'(?<!\\)(?:"""(.*?)"""|\'\'\'(.*?)\'\'\'|"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\')',
        re.DOTALL,
    )
    text = path.read_text(encoding="utf-8", errors="ignore")
    matches = pattern.findall(text)
    results = []
    for m in matches:
        # выбираем непустой вариант из 4 возможных групп
        for group in m:
            if group.strip():
                results.append(group.strip())
                break
    return results


def collect_all_strings(
    base_dir: str, extensions: tuple[str, ...] = (".py",)
) -> dict[str, list[str]]:
    result = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(extensions):
                path = Path(root) / file
                strings = extract_strings_from_file(path)
                if strings:
                    result[str(path)] = strings
    return result


if __name__ == "__main__":
    base_dir = Path(".")
    data = collect_all_strings(str(base_dir))
    output_file = "strings.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Собрано строк: {sum(len(v) for v in data.values())}")
    print(f"Результат сохранён в {output_file}")
