import json
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from PIL import Image, UnidentifiedImageError

from states.models import ArtCraft, Festival, Food, HeritagePlace, HistoricalEvent, State


API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "HeritageAtlasIndiaImageImporter/1.0 (Django management command)"
REQUEST_TIMEOUT = 20
MAX_IMAGE_BYTES = 15 * 1024 * 1024
MIN_IMAGE_WIDTH = 640
MIN_IMAGE_HEIGHT = 360
ALLOWED_FORMATS = {
    "JPEG": ("image/jpeg", ".jpg"),
    "PNG": ("image/png", ".png"),
    "WEBP": ("image/webp", ".webp"),
}
REJECTED_TITLE_TERMS = (
    "logo",
    "icon",
    "flag",
    "map",
    "coat of arms",
    "coat_of_arms",
    "emblem",
    "seal",
)
MODEL_OPTIONS = {
    "state": (State, "State image", "name"),
    "heritage": (HeritagePlace, "Heritage Place", "name"),
    "festival": (Festival, "Festival", "name"),
    "artcraft": (ArtCraft, "Art & Craft", "name"),
    "food": (Food, "Food", "name"),
    "history": (HistoricalEvent, "Historical Event", "title"),
}
MODEL_SEARCH_CONTEXT = {
    "state": "India heritage culture",
    "heritage": "India",
    "festival": "India festival",
    "artcraft": "India traditional craft",
    "food": "India food",
    "history": "India history",
}


class WikimediaError(Exception):
    pass


class WikimediaRateLimit(WikimediaError):
    def __init__(self, message, retry_after):
        super().__init__(message)
        self.retry_after = retry_after


def _retry_delay(value):
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def _request(url, *, max_bytes=None):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            content_type = response.headers.get_content_type()
            if max_bytes is not None:
                if response.headers.get("Content-Length"):
                    if int(response.headers["Content-Length"]) > max_bytes:
                        raise WikimediaError("image exceeds the download size limit")
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise WikimediaError("image exceeds the download size limit")
                return body, content_type
            return response.read(), content_type
    except HTTPError as exc:
        if exc.code == 429:
            retry_header = exc.headers.get("Retry-After")
            retry_after = _retry_delay(retry_header)
            retry_label = retry_header or "not provided"
            raise WikimediaRateLimit(
                f"HTTP 429 rate limit; Retry-After: {retry_label}",
                retry_after,
            ) from exc
        raise WikimediaError(f"HTTP {exc.code}: {exc.reason}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise WikimediaError(str(exc)) from exc


def _plain_metadata_value(metadata, key):
    value = metadata.get(key, {}).get("value", "")
    value = re.sub(r"<[^>]*>", " ", value)
    return " ".join(value.split()).casefold()


def _has_permitted_license(metadata):
    license_name = _plain_metadata_value(metadata, "LicenseShortName")
    attribution_required = _plain_metadata_value(metadata, "AttributionRequired")
    return (
        ("public domain" in license_name or "cc0" in license_name or "cc-zero" in license_name)
        and attribution_required not in {"true", "yes"}
    )


def _candidate_is_suitable(page, image_info):
    title = page.get("title", "").casefold()
    if any(term in title for term in REJECTED_TITLE_TERMS):
        return False, "excluded logo, symbol, map, or flag result"

    if image_info.get("mime") not in {mime for mime, _extension in ALLOWED_FORMATS.values()}:
        return False, "not a supported raster image"

    if (
        image_info.get("width", 0) < MIN_IMAGE_WIDTH
        or image_info.get("height", 0) < MIN_IMAGE_HEIGHT
        or image_info.get("width", 0) < image_info.get("height", 0) * 1.15
    ):
        return False, "image is too small or not landscape"

    metadata = image_info.get("extmetadata", {})
    if not _has_permitted_license(metadata):
        return False, "no public-domain or CC0 license confirmed"

    description = _plain_metadata_value(metadata, "ImageDescription")
    searchable_title = f"{title} {description}"
    if any(term in searchable_title for term in REJECTED_TITLE_TERMS):
        return False, "image description indicates a logo, symbol, map, or flag"

    return True, ""


def _search_image(search_text):
    parameters = urlencode(
        {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": 6,
            "gsrsearch": search_text,
            "gsrlimit": 15,
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
            "iiurlwidth": 1200,
        }
    )
    try:
        response_body, _content_type = _request(f"{API_URL}?{parameters}")
        response_data = json.loads(response_body)
    except WikimediaRateLimit:
        raise
    except (WikimediaError, json.JSONDecodeError) as exc:
        raise WikimediaError(f"Wikimedia search failed: {exc}") from exc

    pages = response_data.get("query", {}).get("pages", {})
    candidates = sorted(pages.values(), key=lambda page: page.get("index", 0))
    last_rejection = "no matching Wikimedia Commons files"

    for page in candidates:
        image_info_list = page.get("imageinfo", [])
        if not image_info_list:
            continue

        image_info = image_info_list[0]
        suitable, reason = _candidate_is_suitable(page, image_info)
        if not suitable:
            last_rejection = reason
            continue

        image_url = image_info.get("thumburl") or image_info.get("url")
        if not image_url:
            last_rejection = "image result has no downloadable URL"
            continue

        try:
            image_bytes, content_type = _request(image_url, max_bytes=MAX_IMAGE_BYTES)
        except WikimediaRateLimit:
            raise
        except WikimediaError as exc:
            last_rejection = f"image download failed: {exc}"
            continue

        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image_format = image.format
                image.verify()
            with Image.open(BytesIO(image_bytes)) as image:
                width, height = image.size
        except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
            last_rejection = "downloaded file is not a valid image"
            continue

        if image_format not in ALLOWED_FORMATS:
            last_rejection = "downloaded image format is not supported"
            continue

        expected_content_type, extension = ALLOWED_FORMATS[image_format]
        if content_type != expected_content_type:
            last_rejection = "downloaded file has an unexpected content type"
            continue
        if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT or width < height * 1.15:
            last_rejection = "downloaded image is too small or not landscape"
            continue

        return image_bytes, extension, page.get("title", "")

    return None, last_rejection


def _state_for(item, model_key):
    return item if model_key == "state" else item.state


def _display_name(item, field_name):
    return getattr(item, field_name)


class Command(BaseCommand):
    help = "Populate empty state and culture ImageFields from Wikimedia Commons."

    def add_arguments(self, parser):
        parser.add_argument("--state", help="Process one state by slug.")
        parser.add_argument(
            "--model",
            choices=tuple(MODEL_OPTIONS),
            help="Limit processing to state, heritage, festival, artcraft, food, or history.",
        )
        parser.add_argument("--limit", type=int, help="Limit the number of missing images processed.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List missing images without making Wikimedia requests or saving files.",
        )

    def handle(self, *args, **options):
        if options["limit"] is not None and options["limit"] < 0:
            raise CommandError("--limit must be zero or greater.")

        states = list(State.objects.all())
        if options["state"]:
            states = [state for state in states if state.slug == options["state"]]
            if not states:
                raise CommandError(f"No state found with slug '{options['state']}'.")
        else:
            states.sort(key=lambda state: (state.slug != "bihar", state.name.casefold()))

        selected_models = (
            (options["model"],)
            if options["model"]
            else tuple(MODEL_OPTIONS)
        )
        missing_items = []

        for state in states:
            for model_key in selected_models:
                model, _label, _field_name = MODEL_OPTIONS[model_key]
                if model_key == "state":
                    if not state.image:
                        missing_items.append((state, model_key))
                    continue

                missing_items.extend(
                    (item, model_key)
                    for item in model.objects.filter(state=state, image="").order_by(
                        MODEL_OPTIONS[model_key][2]
                    )
                )

        if options["limit"] is not None:
            missing_items = missing_items[: options["limit"]]

        total = len(missing_items)
        if not total:
            self.stdout.write(self.style.SUCCESS("No missing images found for the selected scope."))
            return

        for index, (item, model_key) in enumerate(missing_items, start=1):
            state = _state_for(item, model_key)
            model, model_label, field_name = MODEL_OPTIONS[model_key]
            item_name = _display_name(item, field_name)
            progress = f"[{index}/{total}] {state.name} -> {model_label}"
            if model_key != "state":
                progress += f" -> {item_name}"

            if options["dry_run"]:
                self.stdout.write(f"{progress} -> dry-run (missing image)")
                continue

            item.refresh_from_db(fields=["image"])
            if item.image:
                self.stdout.write(f"{progress} -> skipped (image was added by another process)")
                continue

            search_text = (
                f"{state.name} {MODEL_SEARCH_CONTEXT[model_key]}"
                if model_key == "state"
                else f"{item_name} {state.name} {MODEL_SEARCH_CONTEXT[model_key]}"
            )

            rate_limit_retries = 0
            while True:
                try:
                    image_result = _search_image(search_text)
                    break
                except WikimediaRateLimit as exc:
                    rate_limit_retries += 1
                    if (
                        exc.retry_after is None
                        or exc.retry_after > 300
                        or rate_limit_retries > 5
                    ):
                        raise CommandError(
                            f"{progress} -> stopped to respect Wikimedia's rate limit ({exc}). "
                            "Rerun the command later; existing images will be skipped."
                        ) from exc
                    self.stdout.write(
                        f"{progress} -> Wikimedia rate limit; waiting "
                        f"{exc.retry_after:.0f} seconds before retrying."
                    )
                    time.sleep(exc.retry_after)
                except WikimediaError as exc:
                    self.stdout.write(f"{progress} -> skipped (Wikimedia unavailable: {exc})")
                    image_result = (None, str(exc))
                    break

            if image_result[0] is None:
                self.stdout.write(f"{progress} -> skipped/no suitable result ({image_result[1]})")
                continue

            image_bytes, extension, commons_title = image_result
            safe_name = slugify(f"{state.slug}-{item_name}")[:100] or f"{model_key}-{item.pk}"
            filename = f"{safe_name}{extension}"
            try:
                item.image.save(filename, ContentFile(image_bytes), save=True)
            except OSError as exc:
                self.stdout.write(f"{progress} -> skipped (could not save image: {exc})")
                continue

            self.stdout.write(
                self.style.SUCCESS(
                    f"{progress} -> downloaded ({commons_title}; {item.image.name})"
                )
            )

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run complete; no files or database records were changed."))
