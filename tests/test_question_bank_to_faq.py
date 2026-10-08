import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import question_bank_to_faq as converter


def assignment(rows):
    return ("window.questionBank = " + json.dumps(rows, ensure_ascii=False) + ";\n").encode("utf-8")


def row(**changes):
    return {"id": "1", "question": "問題", "answer": "完整答案", **changes}


def csv_rows(data):
    return list(csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True))


class FAQConversionTests(unittest.TestCase):
    def test_actual_bank_complete_ordered_round_trip(self):
        source = (ROOT / "questionBank.js").read_bytes()
        bank = converter.parse_bank(source)
        self.assertEqual(len(bank), 129)
        self.assertEqual(len({item["category"] for item in bank}), 11)
        self.assertEqual(sum("\n" in item["answer"] for item in bank), 47)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "faq.csv"
            report = converter.convert(ROOT / "questionBank.js", output)
            first = output.read_bytes()
            converter.convert(ROOT / "questionBank.js", output)
            self.assertEqual(first, output.read_bytes())
            self.assertEqual(report["records"], 129)
            self.assertEqual(report["input_sha256"], hashlib.sha256(source).hexdigest())
            self.assertEqual(report["output_sha256"], hashlib.sha256(first).hexdigest())
        self.assertEqual(csv_rows(first), [["question", "answer"]] + [
            [item["question"], item["answer"]] for item in bank
        ])
        self.assertTrue(first.startswith(b"question,answer\n"))
        self.assertFalse(first.startswith(b"\xef\xbb\xbf"))

    def test_csv_special_characters_and_whitespace_are_preserved(self):
        fixtures = [
            row(question='  中文,「雙引號"」\n問題  ', answer='\t第一行\r\n第二行, "引用"\r結尾\n'),
            row(id="2", question="https://example.com/?a=1&b=2", answer='<script>原樣純文字</script>'),
            row(id="3", question="=1+1", answer="+SUM(A1:A2)"),
        ]
        bank = converter.parse_bank(assignment(fixtures))
        data = converter.render_csv(bank)
        self.assertEqual(csv_rows(data)[1:], [[x["question"], x["answer"]] for x in fixtures])
        self.assertIn(b'""', data)
        self.assertTrue(data.endswith(b'"\n'))

    def test_bom_and_leading_block_comment(self):
        source = b"\xef\xbb\xbf/* source note */\n" + assignment([row()])
        self.assertEqual(converter.parse_bank(source), [row()])

    def test_optional_metadata_does_not_replace_the_full_answer(self):
        bank = converter.parse_bank(assignment([row(**{"重點摘要": "摘要", "keywords": []})]))
        self.assertEqual(csv_rows(converter.render_csv(bank))[1], ["問題", "完整答案"])

    def test_invalid_unicode_cannot_replace_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source, output = Path(directory) / "bank.js", Path(directory) / "faq.csv"
            source.write_bytes(b'window.questionBank = [{"id":"1","question":"q","answer":"\\ud800"}];')
            output.write_bytes(b"previous output")
            with self.assertRaises(converter.ConversionError):
                converter.convert(source, output)
            self.assertEqual(output.read_bytes(), b"previous output")

    def test_missing_required_fields(self):
        for field in ("id", "question", "answer"):
            with self.subTest(field=field):
                fixture = row()
                del fixture[field]
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(assignment([fixture]))

    def test_null_blank_and_wrong_types(self):
        for field in ("id", "question", "answer"):
            for value in (None, "", " \t\r\n", 1, True, [], {}):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(converter.ConversionError):
                        converter.parse_bank(assignment([row(**{field: value})]))

    def test_duplicate_id_including_surrounding_whitespace(self):
        for duplicate in ("1", " 1 "):
            with self.subTest(duplicate=duplicate):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(assignment([row(), row(id=duplicate, question="另一題")]))

    def test_duplicate_question_including_surrounding_whitespace(self):
        for duplicate in ("問題", " 問題 "):
            with self.subTest(duplicate=duplicate):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(assignment([row(), row(id="2", question=duplicate)]))

    def test_duplicate_object_keys_at_any_depth(self):
        for source in (
            b'window.questionBank = [{"id":"1","id":"2","question":"q","answer":"a"}];',
            b'window.questionBank = [{"id":"1","question":"q","answer":"a","meta":{"x":1,"x":2}}];',
        ):
            with self.subTest(source=source):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(source)

    def test_extra_javascript_is_rejected_without_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "must-not-exist"
            extra = f"require('fs').writeFileSync({json.dumps(str(marker))}, 'executed');".encode()
            for source in (assignment([row()]) + extra, extra + assignment([row()])):
                with self.subTest(source=source):
                    with self.assertRaises(converter.ConversionError):
                        converter.parse_bank(source)
            self.assertFalse(marker.exists())

    def test_dynamic_javascript_is_rejected(self):
        fixtures = (
            b'window.questionBank = getBank();',
            b'window.questionBank = [{"id":"1","question":`q`,"answer":"a"}];',
            b'window.questionBank = [{"id":"1","question":"q","answer":()=>"a"}];',
        )
        for source in fixtures:
            with self.subTest(source=source):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(source)

    def test_malformed_json_and_nonstandard_constants(self):
        for source in (
            b'window.questionBank = [{"id":"1",}];',
            b'window.questionBank = [{"id":"1","question":"q","answer":"a","meta":NaN}];',
            b'window.questionBank = [{"id":"1","question":"q","answer":"a","meta":Infinity}];',
        ):
            with self.subTest(source=source):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(source)

    def test_non_array_empty_array_and_non_object_record(self):
        for fixture in ({}, [], [None], ["row"]):
            with self.subTest(fixture=fixture):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(assignment(fixture))

    def test_utf8_and_exact_assignment_boundary(self):
        for source in (
            b'window.questionBank = [\xff];',
            assignment([row()]).rstrip().removesuffix(b';'),
            assignment([row()]) + b'// trailing executable format not supported',
            assignment([row()]).replace(b'window.questionBank', b'let questionBank'),
        ):
            with self.subTest(source=source):
                with self.assertRaises(converter.ConversionError):
                    converter.parse_bank(source)

    def test_validation_failure_keeps_existing_output_and_creates_no_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "bad.js"
            source.write_bytes(assignment([row(answer="")]))
            output = root / "faq.csv"
            output.write_bytes(b"previous output")
            with self.assertRaises(converter.ConversionError):
                converter.convert(source, output)
            self.assertEqual(output.read_bytes(), b"previous output")
            with self.assertRaises(converter.ConversionError):
                converter.convert(source, root / "new-directory" / "faq.csv")
            self.assertFalse((root / "new-directory").exists())
            self.assertFalse(list(root.glob(".faq-*")))

    def test_replace_failure_keeps_existing_output_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "faq.csv"
            output.write_bytes(b"previous output")
            with patch.object(converter.os, "replace", side_effect=OSError("replace unavailable")):
                with self.assertRaises(OSError):
                    converter.convert(ROOT / "questionBank.js", output)
            self.assertEqual(output.read_bytes(), b"previous output")
            self.assertEqual(list(Path(directory).iterdir()), [output])

    def test_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "bank.js"
            original = assignment([row()])
            source.write_bytes(original)
            with self.assertRaises(converter.ConversionError):
                converter.convert(source, source)
            self.assertEqual(source.read_bytes(), original)

    def test_cli_success_and_failure_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "faq.csv"
            command = [sys.executable, str(ROOT / "tools" / "question_bank_to_faq.py"), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["records"], 129)
            first = output.read_bytes()
            invalid = Path(directory) / "invalid.js"
            invalid.write_bytes(assignment([row(answer=None)]))
            result = subprocess.run(command + ["--input", str(invalid)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertIn("Conversion failed:", result.stderr)
            self.assertEqual(output.read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
