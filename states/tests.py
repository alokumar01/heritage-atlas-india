from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from states.models import State


def _test_landscape_png():
    output = BytesIO()
    Image.new("RGB", (800, 600), color="orange").save(output, format="PNG")
    return output.getvalue()


class PopulateMissingImagesCommandTests(TestCase):
    def setUp(self):
        self.state = State.objects.create(
            name="Example",
            slug="example",
            short_description="",
            description="",
        )

    def test_dry_run_does_not_search_or_save(self):
        with patch(
            "states.management.commands.populate_missing_images._search_image"
        ) as search_image:
            call_command(
                "populate_missing_images",
                "--state",
                self.state.slug,
                "--model",
                "state",
                "--dry-run",
                verbosity=0,
            )

        search_image.assert_not_called()
        self.state.refresh_from_db()
        self.assertFalse(self.state.image)

    def test_downloaded_image_is_saved_to_state_upload_path(self):
        image_bytes = _test_landscape_png()
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch(
                    "states.management.commands.populate_missing_images._search_image",
                    return_value=(image_bytes, ".png", "File:Example heritage.png"),
                ):
                    call_command(
                        "populate_missing_images",
                        "--state",
                        self.state.slug,
                        "--model",
                        "state",
                        verbosity=0,
                    )

                self.state.refresh_from_db()
                self.assertTrue(self.state.image.name.startswith("states/"))
                self.assertTrue(self.state.image.storage.exists(self.state.image.name))
                with self.state.image.open("rb") as saved_image:
                    self.assertEqual(saved_image.read(), image_bytes)

    def test_existing_image_is_not_replaced(self):
        original_image = _test_landscape_png()
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                self.state.image.save(
                    "existing.png",
                    ContentFile(original_image),
                    save=True,
                )
                with patch(
                    "states.management.commands.populate_missing_images._search_image"
                ) as search_image:
                    call_command(
                        "populate_missing_images",
                        "--state",
                        self.state.slug,
                        "--model",
                        "state",
                        verbosity=0,
                    )

                search_image.assert_not_called()
                self.state.refresh_from_db()
                with self.state.image.open("rb") as saved_image:
                    self.assertEqual(saved_image.read(), original_image)
