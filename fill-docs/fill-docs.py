#! /usr/bin/env python3

from gooey import Gooey, GooeyParser
import pypdf
import subprocess
import csv
import argparse
import os


@Gooey
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
        metavar="Column to use for file name:",
        type=int,
        default=0,
        widget="IntegerField",
    )

    args = parser.parse_args()

    with open("input.csv", mode="r", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)

        # ignore header
        next(reader)

        for row in reader:
            name = row[0]
            program = row[1]
            date = row[2]

            data_str = f"""%FDF-1.2
1 0 obj
<<
/FDF << /Fields [
<< /T (Nombre alumno) /V ({name}) >>
<< /T (Programa de estudios) /V ({program}) >>
<< /T (Fecha) /V (and the seal of the university are affixed here. Given at Florida, U.S.A. on Month {date}.) >>
] >>
>>
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""

            data_str = data_str.replace("á", "\\341")
            data_str = data_str.replace("é", "\\351")
            data_str = data_str.replace("í", "\\355")
            data_str = data_str.replace("ó", "\\363")
            data_str = data_str.replace("ú", "\\372")
            data_str = data_str.replace("ñ", "\\361")
            file = open("data.fdf", "w", encoding="utf-8")
            file.write(data_str)
            file.close()

            subprocess.run(
                f'pdftk template.pdf fill_form data.fdf output "./output/{name}.pdf" flatten',
                shell=True,
            )


if __name__ == "__main__":
    main()
