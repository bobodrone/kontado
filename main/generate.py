from _datetime import datetime
import gettext
import os

import pdfkit
from jinja2 import Environment, PackageLoader, select_autoescape
from config import settings
from main.fetchers.invoice_data_fetcher import InvoiceDataFetcher

# gettext.bindtextdomain('kontado', 'locales')
# gettext.textdomain('kontado')
# _ = gettext.gettext
# translations = gettext.find('kontado', 'locales', ['en'])
env = Environment(
    loader=PackageLoader("main", "templates"),
    autoescape=select_autoescape(["html"]),
    #    extensions=['jinja2.ext.i18n']
)
# env.install_gettext_translations(translations)


def generate(me, client, invoice):
    invoices_pdf_path = InvoiceDataFetcher(client).get_pdf_invoices_path()
    if client.language != "sv":
        template = env.get_template(f"base_{client.language}.html")
    else:
        template = env.get_template("base.html")

    invoice.created = invoice.created.strftime("%Y-%m-%d")
    html = template.render(me=me, client=client, invoice=invoice)
    pdf_name = f"{invoice.number}-{client.name}.pdf"
    pdf_path = f"{invoices_pdf_path}/{pdf_name}"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    pdfkit.from_string(
        html,
        pdf_path,
        options={"encoding": "utf8"},
        css=f"{root_dir}/css/stylesheet.css",
    )
