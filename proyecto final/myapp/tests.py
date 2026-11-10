from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.test import TestCase

from . import views


class SponsorshipTests(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.donations_file = Path(self.temp_dir.name) / "donaciones.txt"
        patcher = patch("myapp.views.DONACIONES_FILE", self.donations_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_opening_form_creates_donations_file(self):
        response = self.client.get("/apadrinar/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.donations_file.exists())
        self.assertEqual(self.donations_file.read_text(encoding="utf-8"), "")

    def test_valid_donations_are_appended(self):
        pet = next(pet for pet in views.leer_mascotas() if pet["estado"] != "Adoptada")
        for donor, amount in (("Hanna", "60000"), ("Daniel", "25000")):
            response = self.client.post("/apadrinar/", {
                "animal": pet["nombre"],
                "donor": donor,
                "amount": amount,
            })
            self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.donations_file.read_text(encoding="utf-8").splitlines(),
            [f"Hanna|{pet['nombre']}|60000", f"Daniel|{pet['nombre']}|25000"],
        )

    def test_invalid_donation_is_not_saved(self):
        response = self.client.post("/apadrinar/", {
            "animal": "No existe",
            "donor": "Hanna",
            "amount": "60000",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.donations_file.read_text(encoding="utf-8"), "")
