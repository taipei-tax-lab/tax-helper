"""Convert the static questionBank assignment to deterministic FAQ CSV; never execute JS."""

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[1]
PREFIX = re.compile(r"\A\s*(?:/\*.*?\*/\s*)?window\.questionBank\s*=\s*", re.DOTALL)


class ConversionError(ValueError):
    """The input does not match the supported static format or FAQ schema."""


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ConversionError("JSON object contains a duplicate key")
        obj[key] = value
    return obj


def reject_constant(_value):
    raise ConversionError("Nonstandard JSON numeric constant")


def parse_bank(source):
    try:
        text = source.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ConversionError("Input must be UTF-8") from exc
    prefix = PREFIX.match(text)
    if not prefix:
        raise ConversionError("Expected a single static window.questionBank assignment")
    decoder = json.JSONDecoder(object_pairs_hook=unique_object, parse_constant=reject_constant)
    try:
        bank, end = decoder.raw_decode(text, prefix.end())
    except json.JSONDecodeError as exc:
        raise ConversionError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if text[end:].strip() != ";":
        raise ConversionError("Expected only a semicolon after the JSON array")
    if not isinstance(bank, list) or not bank:
        raise ConversionError("Question bank must be a nonempty JSON array")

    seen = {"id": set(), "question": set()}
    for index, row in enumerate(bank, 1):
        if not isinstance(row, dict):
            raise ConversionError(f"Record {index} must be an object")
        for field in ("id", "question", "answer"):
            value = row.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ConversionError(f"Record {index}: {field} must be a nonempty string")
            # Normalize only the validation key; exported text is never trimmed.
            if field in seen:
                key = value.strip()
                if key in seen[field]:
                    raise ConversionError(f"Record {index}: duplicate {field}")
                seen[field].add(key)
    return bank


def render_csv(bank):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerow(["question", "answer"])
    writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows((row["question"], row["answer"]) for row in bank)
    try:
        data = stream.getvalue().encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ConversionError("Question or answer contains an invalid Unicode surrogate") from exc
    # Check the complete result before any filesystem mutation.
    rows = list(csv.reader(io.StringIO(data.decode("utf-8"), newline=""), strict=True))
    expected = [["question", "answer"]] + [[row["question"], row["answer"]] for row in bank]
    if rows != expected:
        raise ConversionError("CSV round-trip failed")
    return data


def convert(input_path, output_path):
    input_path, output_path = Path(input_path), Path(output_path)
    if input_path.resolve() == output_path.resolve():
        raise ConversionError("Output must not replace the source question bank")
    source = input_path.read_bytes()
    bank = parse_bank(source)
    data = render_csv(bank)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output_path.parent, prefix=".faq-", suffix=".tmp", delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        os.replace(temporary, output_path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return {
        "converter_version": VERSION,
        "records": len(bank),
        "input_sha256": hashlib.sha256(source).hexdigest(),
        "output_sha256": hashlib.sha256(data).hexdigest(),
        "output": str(output_path),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "questionBank.js")
    parser.add_argument("--output", type=Path, default=ROOT / "generated" / "faq.csv")
    args = parser.parse_args(argv)
    try:
        report = convert(args.input, args.output)
    except (ConversionError, OSError) as exc:
        print(f"Conversion failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
