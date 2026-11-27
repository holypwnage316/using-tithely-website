import json
import re
import shutil
from html import escape
from pathlib import Path
from string import Template
from tempfile import TemporaryDirectory
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "site" / "assets"
TEMPLATES = ROOT / "site" / "templates"
GUIDES = ROOT / "content" / "guides"
OUTPUT = ROOT / "dist"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
AUDIENCES = {
    "ministry-leaders": "Ministry leaders",
    "volunteers": "Volunteers",
}


def render(template, **values):
    return Template((TEMPLATES / template).read_text(encoding="utf-8")).substitute(values)


def layout(title, description, content):
    return render("layout.html", title=escape(title), description=escape(description), content=content)


def screenshot(image):
    name = image["file"]
    alt = image["alt"].strip()
    path = ASSETS / "screenshots" / name
    if Path(name).name != name or not path.is_file():
        raise ValueError(f"Screenshot {name!r} must exist in site/assets/screenshots/")
    if not alt:
        raise ValueError(f"Screenshot {name!r} needs alt text")

    url = "/assets/screenshots/" + quote(name)
    caption = escape(image.get("caption", "").strip())
    caption = f"<span>{caption}</span>" if caption else ""
    return f"""              <figure class="screenshot">
                <img src="{url}" alt="{escape(alt)}" loading="lazy">
                <figcaption>{caption}<a href="{url}">Open full-size screenshot</a></figcaption>
              </figure>"""


def guide_page(guide):
    step_links = []
    steps = []
    ids = set()
    for number, step in enumerate(guide["steps"], start=1):
        step_id = step["id"]
        if not SLUG.fullmatch(step_id) or step_id in ids:
            raise ValueError(f"Invalid or duplicate step id {step_id!r}")
        ids.add(step_id)
        title = escape(step["title"])
        step_links.append(f'            <li><a href="#{step_id}">{title}</a></li>')
        body = [f"              <p>{escape(paragraph)}</p>" for paragraph in step["paragraphs"]]
        body.extend(screenshot(image) for image in step.get("images", []))
        body_html = "\n".join(body)
        steps.append(f"""          <li class="guide-step" id="{step_id}">
            <span class="step-number" aria-hidden="true">{number}</span>
            <div>
              <h2>{title}</h2>
{body_html}
            </div>
          </li>""")

    return render(
        "guide.html",
        role=escape(guide["role"]),
        title=escape(guide["title"]),
        summary=escape(guide["summary"]),
        step_links="\n".join(step_links),
        steps="\n".join(steps),
    )


def guide_card(slug, guide, audience_title):
    role = guide["role"]
    role_label = ""
    if role.casefold() != audience_title.casefold():
        role_label = f'\n            <p class="role">{escape(role)}</p>'
    return f"""        <li>
          <a class="guide-card" href="/{slug}/">
            <h3>{escape(guide["title"])}</h3>{role_label}
            <p>{escape(guide["summary"])}</p>
          </a>
        </li>"""


def guide_group(audience, title, cards):
    card_list = "\n".join(cards)
    return f"""      <section class="guide-group" id="{audience}" aria-labelledby="{audience}-title">
        <h2 id="{audience}-title">{title}</h2>
        <ul class="guide-cards" role="list">
{card_list}
        </ul>
      </section>"""


def build():
    with TemporaryDirectory(prefix=".site-build-", dir=ROOT) as temp:
        output = Path(temp) / "dist"
        shutil.copytree(ASSETS, output / "assets", ignore=shutil.ignore_patterns(".gitkeep", ".DS_Store"))
        cards = {audience: [] for audience in AUDIENCES}
        for source in sorted(GUIDES.glob("*.json")):
            slug = source.stem
            try:
                if not SLUG.fullmatch(slug):
                    raise ValueError("Use lowercase words and hyphens in the guide filename")
                guide = json.loads(source.read_text(encoding="utf-8"))
                audience = guide.get("audience", "volunteers")
                if audience not in AUDIENCES:
                    raise ValueError("The audience must be ministry-leaders or volunteers")
                page = layout(f'{guide["title"]} | Mercy PCA', guide["summary"], guide_page(guide))
                cards[audience].append(guide_card(slug, guide, AUDIENCES[audience]))
            except (KeyError, TypeError, ValueError) as error:
                raise SystemExit(f"{source.relative_to(ROOT)}: {error}") from None
            (output / slug).mkdir()
            (output / slug / "index.html").write_text(page, encoding="utf-8")

        groups = "\n".join(
            guide_group(audience, title, cards[audience])
            for audience, title in AUDIENCES.items()
            if cards[audience]
        )
        home = render("home.html", groups=groups)
        (output / "index.html").write_text(
            layout("Tithely guides | Mercy PCA", "Tithely walkthroughs for Mercy PCA ministry leaders and volunteers.", home),
            encoding="utf-8",
        )
        (output / "404.html").write_text(
            layout("Page not found | Mercy PCA", "Browse the Mercy PCA Tithely guide list.", render("404.html")),
            encoding="utf-8",
        )
        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        output.rename(OUTPUT)


if __name__ == "__main__":
    build()
