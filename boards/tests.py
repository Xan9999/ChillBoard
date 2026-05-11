import shutil
import tempfile
from pathlib import Path

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import BackgroundImage
from .models import ProfileImage

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None


TEST_MEDIA_ROOT = str((Path(__file__).resolve().parent.parent / ".test_media").resolve())


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class BackgroundUploadTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def _png(self, color=(255, 0, 0)):
        if Image is None:
            return SimpleUploadedFile("bg.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")
        img = Image.new("RGB", (10, 10), color=color)
        buf = tempfile.SpooledTemporaryFile()
        img.save(buf, format="PNG")
        buf.seek(0)
        return SimpleUploadedFile("bg.png", buf.read(), content_type="image/png")

    def test_background_upload_creates_record(self):
        user = User.objects.create_user(username="u1", password="pass")
        self.client.login(username="u1", password="pass")

        resp = self.client.post("/background/", {"background": self._png()})
        self.assertEqual(resp.status_code, 200)

        bg = BackgroundImage.objects.get(user=user)
        self.assertTrue(bg.background.name)

    def test_background_upload_replaces_file(self):
        user = User.objects.create_user(username="u2", password="pass")
        self.client.login(username="u2", password="pass")

        self.client.post("/background/", {"background": self._png(color=(255, 0, 0))})
        bg1 = BackgroundImage.objects.get(user=user)
        name1 = bg1.background.name

        self.client.post("/background/", {"background": self._png(color=(0, 255, 0))})
        bg2 = BackgroundImage.objects.get(user=user)
        self.assertNotEqual(bg2.background.name, name1)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileUploadTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def _png(self, color=(0, 0, 255)):
        if Image is None:
            return SimpleUploadedFile("p.png", b"\x89PNG\r\n\x1a\n", content_type="image/png")
        img = Image.new("RGB", (10, 10), color=color)
        buf = tempfile.SpooledTemporaryFile()
        img.save(buf, format="PNG")
        buf.seek(0)
        return SimpleUploadedFile("p.png", buf.read(), content_type="image/png")

    def test_profile_upload_creates_record(self):
        user = User.objects.create_user(username="p1", password="pass")
        self.client.login(username="p1", password="pass")

        resp = self.client.post("/profile/", {"image": self._png()})
        self.assertEqual(resp.status_code, 200)

        profile = ProfileImage.objects.get(user=user)
        self.assertTrue(profile.image.name)

    def test_profile_upload_replaces_file(self):
        user = User.objects.create_user(username="p2", password="pass")
        self.client.login(username="p2", password="pass")

        self.client.post("/profile/", {"image": self._png(color=(255, 0, 0))})
        p1 = ProfileImage.objects.get(user=user)
        name1 = p1.image.name

        self.client.post("/profile/", {"image": self._png(color=(0, 255, 0))})
        p2 = ProfileImage.objects.get(user=user)
        self.assertNotEqual(p2.image.name, name1)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class DefaultProfileTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_registered_user_gets_default_images(self):
        resp = self.client.post("/register/", {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(resp.status_code, 302)

        user = User.objects.get(username="newuser")
        profile = ProfileImage.objects.get(user=user)
        background = BackgroundImage.objects.get(user=user)
        self.assertTrue(profile.image.name)
        self.assertTrue(background.background.name)
