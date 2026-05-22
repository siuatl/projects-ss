#! /usr/bin/env python3

# Run command:
# uv run ./fill-diploma-usa.py --ignore-gooey ~/input.xlsx


import sys

from gooey import Gooey, GooeyParser
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject
from pathlib import Path
import pypdf
import unicodedata
import csv
import argparse
import os
import io
import openpyxl
import pymupdf
import template_pdf_base64
import base64


def to_ansi_compatible(text):
    # Normalize 'é' to 'e' + '´' and then encode to ascii
    # 'NFKD' breaks characters into their base components
    normalized = unicodedata.normalize("NFKD", text)
    # Encode to ascii and ignore the leftover accent marks
    return normalized.encode("ascii", "ignore").decode("ascii")


def flatten_and_save_fields(input_pdf):
    doc = pymupdf.open(input_pdf)

    for page in doc:
        # This converts interactive fields (widgets) directly into raw text elements
        # completely flattens annotations and form fields into page paths/text
        page.clean_contents()

    doc.bake()  # flatten PDF
    doc.saveIncr()  # Save cahges to file
    doc.close()


@Gooey(
    show_restart_button=False,
    disable_stop_button=True,
    progress_indicator_type="progressbar",
    progress_regex=r"Processing document (\d+)/(\d+)",
    progress_expr="x[0] / x[1] * 100",
)
def main():
    parser = GooeyParser(
        description="Program to fill the USA diplomas from an Excel file."
    )

    group = parser.add_argument_group("Input Files")

    group.add_argument(
        "input_xlsx",
        metavar="Input Excel(.XLSX) file path:",
        widget="FileChooser",
    )

    args = parser.parse_args()

    wb = openpyxl.load_workbook(args.input_xlsx, data_only=True)
    sheet = wb.active

    csv_file = io.StringIO()
    csv_writer = csv.writer(csv_file, delimiter=",")
    csv_writer.writerows(sheet.iter_rows(values_only=True))

    wb.close()

    csv_file.seek(0)

    reader_count = csv.reader(csv_file)
    total = sum(1 for row in reader_count) - 1

    csv_file.seek(0)

    reader_csv = csv.reader(csv_file)
    header = next(reader_csv)

    input_pdf = io.BytesIO(base64.b64decode(template_pdf_base64.template_pdf_base64))
    reader = PdfReader(input_pdf)
    fields = reader.get_fields()

    print("**Starting to fill PDF files.**", flush=True)
    print(to_ansi_compatible(f"\t-Excel field names: {header}"), flush=True)
    print(to_ansi_compatible(f"\t-PDF field names: {list(fields.keys())}"), flush=True)
    output_path = Path(".") / "output"
    output_path = output_path.resolve()
    print(to_ansi_compatible(f"\t-Writing documents to : {output_path}"), flush=True)
    print("\n", flush=True)
    reader.close()
    input_pdf.seek(0)

    count = 1
    for row in reader_csv:
        reader = PdfReader(input_pdf)
        fields = reader.get_fields()
        writer = PdfWriter()
        writer.append(reader)
        writer.set_need_appearances_writer()

        data_to_fill = dict()
        print(
            to_ansi_compatible(f"Processing document {count}/{total} ('{row[0]}.pdf')"),
            flush=True,
        )
        count += 1

        for (field_name, info), fill_text in zip(fields.items(), row):
            if field_name == "Fecha":
                date_splited = fill_text.split("-")
                data_to_fill[
                    field_name
                ] = f"and the seal of the university are affixed here. Given at Florida, U.S.A. on Month {date_splited[1]}, of {date_splited[0]}."
            else:
                data_to_fill[field_name] = fill_text

        for page in writer.pages:
            writer.update_page_form_field_values(page, data_to_fill, flags=1)

            if "/Annots" in page:
                for annot in page["/Annots"]:
                    obj = annot.get_object()
                    if "/T" in obj:
                        obj.update({NameObject("/Ff"): NumberObject(1)})

        full_path = Path(".") / "output" / f"{row[0]}.pdf"
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            writer.write(f)
            writer.close()
        flatten_and_save_fields(full_path)

        reader.close()
    csv_file.close()

    print("\n**Finished writing all documents.**", flush=True)


if __name__ == "__main__":
    sys.exit(main())
