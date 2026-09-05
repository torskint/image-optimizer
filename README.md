# image-optimizer

Script Python qui convertit des images PNG/JPEG en **AVIF** (format principal, meilleure compression) et **WebP** (secours pour les navigateurs plus anciens), avec redimensionnement optionnel. Pensé pour compresser des visuels de site e-commerce sans toucher aux originaux.

Sur un jeu de 28 bannières/visuels (~72 Mo), le script a permis une réduction de poids d'environ **-98% en AVIF** et **-96% en WebP**.

## Prérequis

- Python 3.10+
- [Pillow](https://python-pillow.org/) avec support AVIF et WebP :

```bash
pip install pillow
```

## Organisation des dossiers

```
stones/
├── optimize_images.py
├── unoptimized/          # images sources (originales, jamais modifiées)
│   ├── bannieres/
│   ├── carre/
│   └── categories/
└── optimise/             # généré par le script
    ├── avif/
    │   ├── bannieres/
    │   ├── carre/
    │   └── categories/
    └── webp/
        ├── bannieres/
        ├── carre/
        └── categories/
```

Le script détecte automatiquement tous les sous-dossiers présents sous `unoptimized/` — pas besoin de le reconfigurer si tu ajoutes un nouveau sous-dossier (ex: `categories/`).

## Utilisation

Depuis la racine du projet :

```bash
python optimize_images.py
```

Cela lit toutes les images (`.png`, `.jpg`, `.jpeg`) de `unoptimized/` et écrit les versions compressées dans `optimise/avif/` et `optimise/webp/`.

### Options

| Option | Défaut | Description |
|---|---|---|
| `sources` (positionnel) | tous les sous-dossiers | Sous-dossiers spécifiques à traiter, relatifs à `--source-root` |
| `--source-root` | `unoptimized` | Dossier de référence contenant les images sources |
| `--output` | `optimise` | Dossier de sortie |
| `--avif-quality` | `50` | Qualité AVIF (0-100) |
| `--webp-quality` | `82` | Qualité WebP (0-100) |
| `--scale` | `1.0` | Facteur de redimensionnement, ratio toujours préservé (ex: `0.5` = moitié des dimensions) |
| `--force` | désactivé | Retraite toutes les images, même celles déjà à jour |

### Exemples

Traiter uniquement le dossier `bannieres/` :

```bash
python optimize_images.py bannieres
```

Redimensionner à moitié et forcer le webp en meilleure qualité :

```bash
python optimize_images.py --scale 0.5 --webp-quality 90
```

Tout retraiter depuis zéro (ex: après avoir changé les paramètres de qualité) :

```bash
python optimize_images.py --force
```

## Comportement incrémental

Le script est réutilisable : si les versions AVIF et WebP d'une image existent déjà et sont plus récentes que le fichier source, elles ne sont pas régénérées. Relance-le après avoir ajouté de nouvelles images dans `unoptimized/` — seules les nouveautés seront traitées.

## Utilisation des images générées en HTML

Sers l'AVIF en priorité avec le WebP en repli via `<picture>` :

```html
<picture>
  <source srcset="optimise/avif/bannieres/Container.avif" type="image/avif">
  <img src="optimise/webp/bannieres/Container.webp" alt="Container">
</picture>
```
