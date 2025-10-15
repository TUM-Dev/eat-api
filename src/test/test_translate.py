import pathlib
import tempfile

from src.entities import Canteen
from src.translate import Translator, translate_file
from src.utils.file_util import load_ordered_json


class TestTranslate:
    base_path = pathlib.Path("src/test/assets/studentenwerk") / Canteen.MENSA_GARCHING.canteen_id

    def test_week(self):
        input_file = self.base_path / "reference/week_31.json"
        expected_file = self.base_path / "en/week_31.json"

        translator = Translator("DUMMY", self.base_path / "en/translations.json")
        translator.load_cache()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = pathlib.Path(temp_dir) / "week_31.json"
            translate_file(input_file, output, translator)
            translated = load_ordered_json(output)

        expected = load_ordered_json(expected_file)
        assert translated == expected

    def test_combined(self):
        input_file = self.base_path / "reference/combined.json"
        expected_file = self.base_path / "en/combined.json"

        translator = Translator("DUMMY", self.base_path / "en/translations.json")
        translator.load_cache()
        with tempfile.TemporaryDirectory() as temp_dir:
            output = pathlib.Path(temp_dir) / "combined.json"
            translate_file(input_file, output, translator)
            translated = load_ordered_json(output)

        expected = load_ordered_json(expected_file)
        assert translated == expected
