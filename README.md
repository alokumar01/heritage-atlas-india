# Heritage Atlas India

## Ideas that showcase the rich cultural heritage and traditions of India

Heritage Atlas India is a digital exploration platform that lets visitors
discover India's cultural heritage state by state.

The project brings together heritage places, festivals, traditional arts and
crafts, regional food, and historical events in one responsive experience.

---

## Project Objective

The objective is to make India's diverse cultural heritage easier to explore
through a visual, interactive, state-wise website. Visitors can move from an
overview of India to a state and then explore that state's places, traditions,
arts, food, and history.

---

## Main Features

- State-wise exploration of India's 28 states
- Clickable India SVG map
- State search and region filtering
- Dedicated state detail pages
- Heritage places, festivals, arts and crafts, food, and historical events
- State and content images, with visual fallbacks where images are absent
- Previous/next state navigation
- Responsive mobile navigation and layouts
- Django admin content management
- Optional Wikimedia Commons image search for records without images

Image coverage is not complete for every individual content record. The site
uses designed fallbacks for records without an uploaded image.

---

## Technology Stack

### Backend

- Python
- Django
- SQLite (the configured local development database)
- Pillow for image-field validation

### Frontend

- Django templates and HTML
- Tailwind CSS
- JavaScript
- SVG map

### Development Tools

- npm
- Git and GitHub

---

## Project Structure

```text
heritage-atlas-india/
├── config/                         Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/                           Home, Explore, and About pages
│   ├── views.py
│   └── templates/core/
├── states/                         State and cultural content app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── management/commands/        Optional image-population command
│   ├── migrations/
│   └── templates/states/
├── templates/
│   ├── base.html                   Shared navigation and footer
│   └── components/                 Shared cards and map templates
├── static/
│   ├── css/
│   ├── js/
│   ├── src/                        Tailwind input stylesheet
│   └── images/                     Site hero and map assets
├── media/                          User-uploaded model images (local, ignored)
├── staticfiles/                    collectstatic output (generated, ignored)
├── manage.py
├── package.json
├── package-lock.json
├── requirements.txt
├── .gitignore
└── README.md
```

The local SQLite database, `.env`, uploaded media, collected static output,
virtual environment, and `node_modules` are excluded from Git. A fresh clone
does not include the local development database or uploaded media files.

---

## Database Models

The main models are:

- `State`
- `HeritagePlace`
- `Festival`
- `ArtCraft`
- `Food`
- `HistoricalEvent`

Each content model has a `ForeignKey` to `State`. One state can have many
related content records, while each individual content record belongs to one
state. The reverse relation names provide convenient access, for example:

```python
state.heritage_places.all()
state.festivals.all()
state.arts_crafts.all()
state.foods.all()
state.historical_events.all()
```

---

## Main Pages

### Home

Introduces the project, links to Explore, and highlights state cards.

### Explore

Provides state search, region filtering, a clickable India map, and state
cards.

### State Detail

Shows a state's description and its heritage places, festivals, arts and
crafts, food, and historical events, along with navigation to adjacent states.

### About

Explains the project's idea, subject areas, and vision.

### Admin

Allows authorized administrators to create and manage states and related
cultural content at `/admin/`.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/alokumar01/heritage-atlas-india.git
cd heritage-atlas-india
```

Create and activate a Python virtual environment.

### Linux and macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file beside `manage.py`. Generate a Django secret key
without committing it:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Put the generated value into `.env`:

```dotenv
SECRET_KEY=paste-your-generated-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

The `.env` file is ignored by Git. Do not commit it or share its secret key.

Install frontend dependencies and apply migrations:

```bash
npm install
python manage.py migrate
```

Start Tailwind in one terminal:

```bash
npm run dev
```

Start Django in another terminal:

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

The database and uploaded images are local files and are not included in a
fresh clone. Add records through Django admin or another approved data-loading
workflow, and upload media as needed.

---

## Admin

Create an administrator interactively:

```bash
python manage.py createsuperuser
```

Then sign in at <http://127.0.0.1:8000/admin/>. Do not store admin passwords
in source code or this README.

---

## Optional Image Population

The project includes a management command that searches Wikimedia Commons for
images for records whose image field is empty. It skips existing images,
validates downloaded files, and only accepts confirmed public-domain or CC0
results. Some records may remain without an image when no suitable result is
available.

Preview missing-image records without making network requests:

```bash
python manage.py populate_missing_images --dry-run
```

To attempt population for one state:

```bash
python manage.py populate_missing_images --state bihar
```

Wikimedia may rate-limit requests. The command respects the supplied retry
delay; it can take time to process many records.

---

## Checks and Static Files

Run the Django checks and tests:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Collect static files for deployment:

```bash
python manage.py collectstatic --noinput
```

`staticfiles/` is generated output and is ignored by Git. HTTPS-only settings
(HSTS, secure cookies, and SSL redirects) should only be enabled when the
deployment is configured to serve the site over HTTPS. Configure a real SMTP
provider through environment variables before relying on email delivery.

---

## Demo Sequence

Use this sequence for a short project demonstration:

1. Home: introduce the project and its entry points.
2. Explore: search for Bihar and show the matching state result.
3. Open Bihar and explain the state summary and capital/region information.
4. Show Heritage, Festivals, Arts & Crafts, Food, and History.
5. Demonstrate the previous/next state links.
6. Return to Explore and use the map or region filter.
7. Open About.
8. Open Admin and show the available content models.

### Suggested Submission Screenshots

- Home page: hero, state cards, and final call to action
- Explore page: search, map, and state cards
- Bihar state page: hero, state information, and heritage places
- Bihar state page: festivals, arts and crafts, food, and history
- About page
- Django admin model list

Capture screenshots from the browser after running the project locally. Avoid
including private `.env` contents or account credentials.

---

## Architecture Viva Notes

The request flow is:

```text
Browser request
    ↓
URL route
    ↓
Django view
    ↓
ORM query and related models
    ↓
Template context
    ↓
Django template
    ↓
HTML response
```

For example, `/states/bihar/` matches the slug route in `states/urls.py`.
`state_detail()` looks up the state with `get_object_or_404()`, fetches its
related content through Django's ORM, and passes the objects to
`states/templates/states/state_detail.html`.

### Database Relationship

```text
State
├── HeritagePlace
├── Festival
├── ArtCraft
├── Food
└── HistoricalEvent
```

The `ForeignKey` means one state can have many content records. For example,
`related_name='festivals'` enables `state.festivals.all()`.

### Dynamic Content

State pages share one template. The URL's state slug selects the database
record; the view passes that state and its related objects into the template.
The template loops over those objects, so state content is data-driven rather
than hard-coded separately for every state.

### Useful Viva Topics

- Django URL routing and named routes
- Views, context, and templates
- Models and `ForeignKey` relationships
- Django ORM filtering and related managers
- Slugs and `get_object_or_404()`
- Django admin content management
- Static assets versus uploaded media
- Responsive layout and empty/image fallback states

---

## Future Scope

- More detailed and reviewed heritage content
- More contextually verified images and multimedia
- Interactive historical timelines
- Expanded map interactions
- Multilingual content
- PostgreSQL and cloud deployment
- User accounts, bookmarks, and personalized exploration

---

## Project Status

Heritage Atlas India is a Django-based cultural heritage exploration project.
It includes state-wise pages, related cultural content, an interactive map,
admin management, and responsive layouts. Content and image coverage can
continue to grow.
