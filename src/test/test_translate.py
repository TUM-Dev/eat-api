import pathlib
import tempfile

import pytest
from syrupy.extensions.json import JSONSnapshotExtension

from src.entities import Canteen
from src.translate import Translator, translate_file
from src.utils.file_util import load_ordered_json


@pytest.fixture
def snapshot_json(snapshot):
    return snapshot.with_defaults(extension_class=JSONSnapshotExtension)


class TestTranslate:
    base_path = pathlib.Path("src/test/assets/studentenwerk") / Canteen.MENSA_GARCHING.canteen_id

    def test_week(self, snapshot_json):
        input_file = self.base_path / "reference/week_31.json"

        translator = Translator("DUMMY", self.base_path / "en/translations.json")
        translator.load_cache()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = pathlib.Path(temp_dir) / "week_31.json"
            translate_file(input_file, output, translator)
            translated = load_ordered_json(output)

        assert translated == snapshot_json

    def test_combined(self, snapshot_json):
        input_file = self.base_path / "reference/combined.json"

        translator = Translator("DUMMY", self.base_path / "en/translations.json")
        translator.load_cache()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = pathlib.Path(temp_dir) / "combined.json"
            translate_file(input_file, output, translator)
            translated = load_ordered_json(output)

        assert translated == snapshot_json
