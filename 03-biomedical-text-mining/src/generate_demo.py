"""Generate explicitly fictional demonstration notes (not real clinical records)."""
from pathlib import Path

DEMO = {
    "demo_01.txt": "Fictional example. Patient discusses diabetes management. Follow-up planned in two weeks. Diabetes education reviewed.",
    "demo_02.txt": "Fictional example. Hypertension monitoring visit. Return for f/u after four weeks. No diagnosis of diabetes documented.",
    "demo_03.txt": "Fictional example. Respiratory symptoms assessed. Follow up as needed; supportive care instructions discussed.",
    "demo_04.txt": "Fictional example. Diabetes screening results discussed. Education and medication review completed.",
    "demo_05.txt": "Fictional example. Routine wellness assessment. No specific follow-up interval documented.",
}


def generate(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in DEMO.items():
        (folder / name).write_text(text + "\n", encoding="utf-8")
    print(f"Generated {len(DEMO)} fictional documents in {folder}")


if __name__ == "__main__":
    generate(Path("data/demo_texts"))
