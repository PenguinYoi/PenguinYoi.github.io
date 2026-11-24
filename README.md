# Jake’s field notes

Personal academic website for PenguinYoi.github.io.

## Edit text

Open https://penguinyoi.github.io/admin/ and follow the link to Pages CMS. Sign in with GitHub, choose PenguinYoi/PenguinYoi.github.io on main, then edit About & introduction, Projects, Experience, or Contact & links. Saving makes a Git commit and the Publish academic website workflow deploys the result. No HTML editing is needed. GitHub App installation must be authorized for this repository first. Do not add CMS collaborators if you want sole editing access.

The admin landing page is public; edit access is enforced by Pages CMS and GitHub repository permissions. Public repository content and history are public. This version saves directly to main and has no private drafts or unpublished visual preview. Check the live site after the workflow succeeds. History is available in GitHub for recovery.

## Files

- content/*.json: source of truth for editable content.
- .pages.yml: form definitions (JSON syntax, valid YAML).
- templates/index.html: site layout.
- scripts/build.py: HTML-escaping renderer and public artifact builder.
- styles.css, script.js: presentation and motion.
- .github/workflows/publish.yml: test, build, publish workflow.

Run `python3 scripts/build.py` to create index.html and _site/. Preview with `python3 -m http.server 8033 --directory _site`. Run `python3 -m unittest discover -s scripts -p 'test_*.py' -v` for content-rendering tests.

GitHub Pages source must be GitHub Actions. Only generated _site/ assets are deployed; content source and schema remain available in the public GitHub repository. No credentials are stored in site files.
