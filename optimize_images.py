#!/usr/bin/env python3
"""Convertit les images PNG/JPEG du dossier de référence (unoptimized/) en AVIF (principal) + WebP (secours).

Usage:
    python optimize_images.py [sous-dossiers...] [--source-root unoptimized] [--avif-quality 50] [--webp-quality 82] [--output optimise] [--force]
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

SOURCE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
FORMATS = [
    ("avif", "AVIF"),
    ("webp", "WEBP"),
]


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("o", "Ko", "Mo", "Go"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} To"


def discover_source_dirs(source_root: Path) -> list[Path]:
    return sorted(
        d for d in source_root.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def convert_image(src: Path, dst_avif: Path, dst_webp: Path, avif_quality: int, webp_quality: int, scale: float) -> dict:
    dst_avif.parent.mkdir(parents=True, exist_ok=True)
    dst_webp.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        if scale != 1.0:
            new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
            img = img.resize(new_size, Image.LANCZOS)
        img.save(dst_avif, "AVIF", quality=avif_quality)
        img.save(dst_webp, "WEBP", quality=webp_quality, method=6)
    return {
        "before": src.stat().st_size,
        "avif": dst_avif.stat().st_size,
        "webp": dst_webp.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sources", nargs="*",
        help="Sous-dossiers à traiter, relatifs à --source-root (défaut : tous les sous-dossiers)",
    )
    parser.add_argument("--source-root", default="unoptimized", help="Dossier de référence contenant les images sources (défaut: unoptimized)")
    parser.add_argument("--avif-quality", type=int, default=50, help="Qualité AVIF (0-100, défaut 50)")
    parser.add_argument("--webp-quality", type=int, default=82, help="Qualité WebP de secours (0-100, défaut 82)")
    parser.add_argument("--output", default="optimise", help="Dossier de sortie (défaut: optimise)")
    parser.add_argument("--scale", type=float, default=1.0, help="Facteur de redimensionnement, ratio préservé (défaut 1.0, ex: 0.5 pour moitié)")
    parser.add_argument("--force", action="store_true", help="Retraiter même si déjà à jour")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    source_root = root / args.source_root
    output_root = root / args.output

    if not source_root.is_dir():
        print(f"Dossier de référence introuvable : {source_root}", file=sys.stderr)
        return 1

    source_dirs = (
        [source_root / s for s in args.sources] if args.sources
        else discover_source_dirs(source_root)
    )

    missing = [d for d in source_dirs if not d.is_dir()]
    if missing:
        print(f"Dossier(s) introuvable(s) : {', '.join(str(d) for d in missing)}", file=sys.stderr)
        return 1

    total_before = 0
    total_avif = 0
    total_webp = 0
    converted = 0
    skipped = 0

    for src_dir in source_dirs:
        rel_dir = src_dir.relative_to(source_root)
        for src in sorted(src_dir.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in SOURCE_EXTENSIONS:
                continue

            rel = src.relative_to(src_dir)
            dst_avif = output_root / "avif" / rel_dir / rel.with_suffix(".avif")
            dst_webp = output_root / "webp" / rel_dir / rel.with_suffix(".webp")

            up_to_date = (
                not args.force
                and dst_avif.exists() and dst_avif.stat().st_mtime >= src.stat().st_mtime
                and dst_webp.exists() and dst_webp.stat().st_mtime >= src.stat().st_mtime
            )
            if up_to_date:
                skipped += 1
                continue

            sizes = convert_image(src, dst_avif, dst_webp, args.avif_quality, args.webp_quality, args.scale)
            total_before += sizes["before"]
            total_avif += sizes["avif"]
            total_webp += sizes["webp"]
            converted += 1
            reduction = 100 * (1 - sizes["avif"] / sizes["before"]) if sizes["before"] else 0
            print(
                f"{src.relative_to(source_root)}: {human_size(sizes['before'])} "
                f"-> avif {human_size(sizes['avif'])} / webp {human_size(sizes['webp'])} (-{reduction:.0f}% en avif)"
            )

    print()
    if converted:
        avif_reduction = 100 * (1 - total_avif / total_before) if total_before else 0
        webp_reduction = 100 * (1 - total_webp / total_before) if total_before else 0
        print(f"{converted} image(s) converties depuis {human_size(total_before)} :")
        print(f"  AVIF : {human_size(total_avif)} (-{avif_reduction:.0f}%)")
        print(f"  WebP : {human_size(total_webp)} (-{webp_reduction:.0f}%, secours pour anciens navigateurs)")
    if skipped:
        print(f"{skipped} image(s) déjà à jour, ignorées.")
    if not converted and not skipped:
        print("Aucune image trouvée.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
