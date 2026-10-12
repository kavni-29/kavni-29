# Profile README assets

## Layout

- `assets/hero/botanical-loop.gif` is the small animated hero illustration.
- `assets/hero/botanical-static.svg` is its lightweight editable still version and can replace the GIF in the README when a static image is preferred.
- `assets/projects/` contains explanatory diagrams for the two project cards. They are diagrams, not screenshots of the applications.

## Editing the profile

The README is written in Markdown with small HTML tables for its editorial layout. To add a project, copy one project cell in the “On the worktable” table, update its title, link, short evidence-based description, technologies, and diagram, then keep the two cells balanced. Only label work as ongoing or complete when the repository supports that status. Update technology names to match actual project use.

Use local relative paths for artwork. Keep descriptive alt text; label explanatory artwork as diagrams. Keep contact links to GitHub and LinkedIn. Do not add statistics widgets unless there is a clear benefit and a dependable fallback.

## Lightweight assets

All essential artwork is stored in this repository. The SVGs are editable source files; the GIF is a self-contained animation. No build step, JavaScript, custom CSS, or external image service is required. GitHub may render SVG differently from a full browser, so preserve a useful first frame and readable static content.
