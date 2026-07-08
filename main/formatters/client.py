""" Client formatters"""
from .formatters import TableFormatter


class ClientListTableFormatter(TableFormatter):
    """Class Client formatter"""

    def format_table(self, data):
        self.table.add_column("No", style="cyan")
        self.table.add_column("Client name")
        self.table.add_column("Client folder")

        index = 0
        for client in data:
            index = index + 1
            self.table.add_row(f"{index}", client.label, client.name)


class ClientTableFormatter(TableFormatter):
    """Class inherits from Table formatter"""

    def client_info(self, data):
        """Add client info data"""
        return [
            f"{data.label} ({data.name})",
            data.description,
        ]

    def company_info(self, data):
        """Add company info"""
        return [
            f"Org nr: {data.company_info.orgnr}",
            f"VAT nr: {data.company_info.vatnr}",
            "",
        ]

    def format_table(self, data):
        self.table.add_column("Client")
        self.table.add_column("Company info")
        self.table.add_column("Contacts")
        company_info = []
        addresses = [
            ("postal_address", "Postal address"),
            ("visitor_address", "Visitor address"),
        ]
        for address in addresses:
            temp_address = []
            addr = getattr(data.company_info, address[0])

            temp_address = TableFormatter.append_to_list(
                temp_address, addr.co, f"c/o: {addr.co}"
            )
            temp_address = TableFormatter.append_to_list(
                temp_address, addr.thoroughfare
            )
            temp_address = TableFormatter.append_to_list(temp_address, addr.premise)

            zip_n_address = []
            zip_n_address = TableFormatter.append_to_list(
                zip_n_address, addr.postalcode
            )
            zip_n_address = TableFormatter.append_to_list(zip_n_address, addr.locality)

            temp_address = TableFormatter.append_to_list(
                temp_address, zip_n_address, " ".join(zip_n_address)
            )

            temp_address = TableFormatter.append_to_list(temp_address, addr.region)
            temp_address = TableFormatter.append_to_list(temp_address, addr.country)

            company_info = self.company_info(data)
            if temp_address:
                company_info = company_info + [
                    f"{address[1]}:",
                    "\n".join(temp_address),
                    "",
                ]

        contacts = []
        if data.contacts:
            for contact in data.contacts:
                temp_contact = []

                temp_contact = TableFormatter.append_to_list(
                    temp_contact, contact.person, f"Name: {contact.person}"
                )
                temp_contact = TableFormatter.append_to_list(
                    temp_contact, contact.title, f"Title: {contact.title}"
                )
                temp_contact = TableFormatter.append_to_list(
                    temp_contact, contact.email, f"E-mail: {contact.email}"
                )
                temp_contact = TableFormatter.append_to_list(
                    temp_contact, contact.phone, f"Phone: {contact.phone}"
                )
                if temp_contact:
                    contacts.append("\n".join(temp_contact))

        invoice_emails = []
        if data.invoice_emails:
            for invoice_email in data.invoice_emails:
                invoice_emails.append(invoice_email)

        if invoice_emails:
            invoice_emails.insert(0, "invoice_emails:")
            contacts.append("\n".join(invoice_emails))

        self.table.add_row(
            "\n".join(self.client_info(data)),
            "\n".join(company_info),
            "\n\n".join(contacts),
        )
