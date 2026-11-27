# Mercy PCA Tithely Guides

A training site for Mercy PCA volunteers and ministry coordinators. Each guide has a shareable URL, links to individual steps, and space for the church’s own screenshots.

| Guide | Shareable path |
| --- | --- |
| Email all nursery volunteers | `/email-nursery-volunteers/` |
| Respond to an RSVP email | `/respond-to-rsvp/` |

## Add your screenshots and instructions

1. Save your screenshots in `site/assets/screenshots/`. For public guides, use a test invitation or crop out personal details and links that can respond to a real assignment.
2. Open the guide’s file in `content/guides/` and edit the `paragraphs` for the step you want to update. Use the labels from your Mercy PCA screens.
3. Add the filename, a short description for screen readers, and an optional visible caption to the step’s `images` list. List multiple images in the order they should appear. An empty list leaves the step as text.

```json
"images": [
  {
    "file": "volunteer-rsvp.png",
    "alt": "Volunteer scheduling email showing the service date and response buttons",
    "caption": "The response buttons are below the service details."
  }
]
```

To create a guide, copy one of the JSON files, give it a new lowercase hyphenated filename, and edit the role, title, summary, and steps. The filename becomes the URL, and the homepage lists the guide automatically. Step IDs become the links in the guide’s table of contents. Keep existing filenames and step IDs when editing a guide you’ve already shared.

## Run locally

```sh
python3 scripts/build.py
python3 -m http.server --bind 127.0.0.1 --directory dist 8000
```

Open [localhost:8000](http://127.0.0.1:8000/). Run the build again after editing content or adding screenshots.

## Deploy to Cloudflare Pages

In Cloudflare, open **Workers & Pages**, choose **Create application**, select the **Pages** tab, and import the [GitHub repository](https://github.com/holypwnage316/using-tithely-website). Use these settings.

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Framework preset | None |
| Root directory | Repository root (default) |
| Build command | `python3 scripts/build.py` |
| Build output directory | `dist` |

The build uses Python’s standard library. Once the first deployment finishes, use the Cloudflare `pages.dev` address with the guide paths above. [Cloudflare Pages static HTML instructions](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/)
