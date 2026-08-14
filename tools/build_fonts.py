from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT.parent
OUT = ROOT / "assets" / "fonts"

UNICODES = ",".join([
    "U+0020-007E",
    "U+00A0-00FF",
    "U+0100-017F",
    "U+0192",
    "U+02C6-02DC",
    "U+2000-206F",
    "U+20AC,U+20A6",
    "U+2122",
    "U+2190-2193",
    "U+2212",
    "U+25CF,U+2022",
])

JOBS = [
    ("junicode-1/Junicode.ttf",            "junicode-regular.woff2"),
    ("junicode-1/Junicode-Italic.ttf",     "junicode-italic.woff2"),
    ("junicode-1/Junicode-Bold.ttf",       "junicode-bold.woff2"),
    ("junicode-1/Junicode-BoldItalic.ttf", "junicode-bolditalic.woff2"),
]

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    missing, total_in, total_out = [], 0, 0

    for src_rel, out_name in JOBS:
        src = SOURCES / src_rel
        if not src.exists():
            missing.append(src_rel)
            continue
        dst = OUT / out_name
        subprocess.run(
            [
                sys.executable, "-m", "fontTools.subset", str(src),
                f"--unicodes={UNICODES}",
                "--layout-features=kern,liga,clig,calt,ccmp,locl,mark,mkmk",
                "--flavor=woff2",
                "--desubroutinize",
                f"--output-file={dst}",
            ],
            check=True,
        )
        total_in += src.stat().st_size
        total_out += dst.stat().st_size
        print(f"  {src.name:32s} {src.stat().st_size/1024:7.1f} KB  ->  "
              f"{out_name:26s} {dst.stat().st_size/1024:6.1f} KB")

    if missing:
        print("\nNo encontrados (¿moviste los directorios de fuentes?):")
        for m in missing:
            print(f"  - {SOURCES / m}")

    if total_in:
        print(f"\nTotal: {total_in/1024:.0f} KB -> {total_out/1024:.0f} KB "
              f"({100 - 100*total_out/total_in:.0f}% menos)")
    return 1 if missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
