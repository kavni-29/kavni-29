# Profile README assets

## Files

- `assets/hero/journal-cover.svg` is the warm-paper editorial masthead shown at the top of the README. Its text and botanical illustration are editable SVG elements.
- `assets/hero/botanical-loop.gif` is the optional, restrained hero animation linked from the README.
- `assets/hero/botanical-static.svg` is the editable still version of that animation.
- `assets/projects/` contains explanatory SVG diagrams for the project cards. They are diagrams, not product screenshots.
- `scripts/profile_assets.py` regenerates the animated hero and checks the README's local artwork references, SVG syntax and palette, and GIF dimensions, frame count, and file size.

The palette is defined at the top of `scripts/profile_assets.py`: ivory `#F6F3EC`, sand `#E8E2D9`, plum `#806784`, dusty rose `#C99AA9`, sage `#91B7AE`, terracotta `#B98E79`, and charcoal `#292725`. When adjusting the palette, update the colours in the static SVG and project diagrams too; run the checker to catch colours outside the palette.

## Regenerate and check

Python 3 and Pillow are needed only to regenerate the GIF. They are not needed to view the GitHub profile. From the repository root:

```powershell
python -m pip install Pillow
python scripts/profile_assets.py build
python scripts/profile_assets.py check
```

Or run both actions together with `python scripts/profile_assets.py all`. The generator uses deterministic geometry and a fixed frame sequence, and writes only `assets/hero/botanical-loop.gif`. The SVG artwork remains directly editable without a build step. No server, API key, framework, JavaScript, or external image service is involved.

## Update project cards

Edit the relevant cell in the “Project exhibits” table in `README.md`. Keep each project description concise and evidence-based, update its technology list to match the repository, and avoid status labels unless the project's state is verified. Edit the corresponding SVG in `assets/projects/` when its process diagram needs to change. Preserve descriptive alt text and use the seven palette colours above.

The project and skills panels are simple HTML tables for GitHub's README renderer. The editorial masthead has descriptive alt text. The animation is optional and the still illustration is available separately. No visitor needs to run the asset script.
