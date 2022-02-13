"""Defines functionality to export JSON data to an HTML template."""

from pathlib import Path
import logging

from global_helpers import get_time_stamp

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2021, Martin Woelke'

REPORT_TEMPLATE = Path('data/report.tpl')

# Currently not used. The CSS is embedded in the template.
CSS_FILE = Path('data/w3.css')


def generate_html_report(report_locations: list):
    """ Generates an HTML report from a template with pre-generated JSON data.

    Loads an HTML template and replaces markers with given JSON data.

    :param report_locations: A list of tuples (path to JSON file and marker name).
    :return: The location of the generated report file or -1 for any error cases.
    """

    logger = logging.getLogger('HTMLExporter')
    template_text = REPORT_TEMPLATE.read_text(encoding="utf-8")

    for data_tuple in report_locations:
        json_file = Path(data_tuple[0])
        json_data = ""

        if json_file.is_file():
            json_data = json_file.read_text(encoding="utf-8")
        else:
            logger.error(f'Unable to load JSON file [{json_file}]')
            return -1

        template_text = template_text.replace(data_tuple[1], json_data)

    report_file = Path(f'reports/report_{get_time_stamp()}.html')
    report_file.write_text(template_text, encoding="utf-8")

    return report_file
