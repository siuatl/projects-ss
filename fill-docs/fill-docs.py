#! /usr/bin/env python3

# Run command:
# uv run ./fill-docs.py --ignore-gooey ./template.pdf ./input.csv

from gooey import Gooey, GooeyParser
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject
from pathlib import Path
import pypdf
import subprocess
import csv
import argparse
import os
import sys


@Gooey(
    show_restart_button=False,
    disable_stop_button=True,
    progress_indicator_type="progressbar",
    progress_regex=r"Processing document (\d+)/(\d+)",
    progress_expr="x[0] / x[1] * 100",
)
def main():
    parser = GooeyParser(description="Program to fill pdf fields from a csv file.")

    group = parser.add_argument_group("Input Files")
    group.add_argument(
        "input_pdf",
        metavar="Input PDF file path:",
        widget="FileChooser",
    )
    group.add_argument(
        "input_csv",
        metavar="Input CSV file path:",
        widget="FileChooser",
    )
    group.add_argument(
        "--file-name-column",
        metavar="Column index to use for output file name:",
        type=int,
        default=0,
        widget="IntegerField",
    )

    args = parser.parse_args()

    with open(args.input_csv, mode="r", encoding="utf-8") as csv_file:
        reader_csv = csv.reader(csv_file)

        header = next(reader_csv)

        reader = PdfReader(args.input_pdf)
        fields = reader.get_fields()

        print("**Starting to fill PDF files.**", file=sys.stderr, flush=True)
        print(f"\t-CSV field names: {header}", file=sys.stderr, flush=True)
        print(f"\t-PDF field names: {list(fields.keys())}", file=sys.stderr, flush=True)
        output_path = Path(".") / "output"
        output_path = output_path.resolve()
        print(f"\t-Writing documents to : {output_path}", file=sys.stderr, flush=True)
        print("\n", file=sys.stderr, flush=True)

        with open(args.input_csv, mode="r", encoding="utf-8") as csv_file_count:
            reader_count = csv.reader(csv_file_count)
            total = sum(1 for row in reader_count) - 1
        count = 1
        for row in reader_csv:
            writer = PdfWriter()
            writer.append(reader)

            data_to_fill = dict()
            print(
                f"Processing document {count}/{total} ('{row[args.file_name_column]}.pdf')",
                file=sys.stderr,
                flush=True,
            )
            count += 1

            for (field_name, info), fill_text in zip(fields.items(), row):
                data_to_fill[field_name] = fill_text

            for page in writer.pages:
                writer.update_page_form_field_values(page, data_to_fill)

                if "/Annots" in page:
                    for annot in page["/Annots"]:
                        obj = annot.get_object()
                        if "/T" in obj:
                            obj.update({NameObject("/Ff"): NumberObject(1)})

            full_path = Path(".") / "output" / f"{row[args.file_name_column]}.pdf"
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "wb") as f:
                writer.write(f)

    print("\n**Finished writing all documents.**", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
