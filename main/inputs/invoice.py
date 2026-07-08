import re

from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.prompt import Confirm


class KPrompt(Prompt):
    def check_choice(self, value: str) -> bool:
        """Check value is in the list of valid choices.

        Args:
            value (str): Value entered by user.

        Returns:
            bool: True if choice was valid, otherwise False.
        """
        assert self.choices is not None
        clean = True
        selected = re.split(",\s?", value.strip())
        for v in selected:
            if v.strip() not in self.choices:
                clean = False
        return clean


class InvoiceInput:
    """Class to handle the task object"""

    @staticmethod
    def ask_invoice_freeform():
        return Confirm.ask(
            "Would you like to create a free-form invoice", default=False
        )

    @staticmethod
    def ask_invoice_freeform_more_line_items():
        return Confirm.ask("Are you done creating line items", default=True)

    @staticmethod
    def ask_select_invoice(choices):
        return IntPrompt.ask("[green]Please select an invoice", choices=choices)

    @staticmethod
    def ask_select_invoices(choices: list):
        invoices = []
        selected = KPrompt.ask(
            "[green]Select invoices above, pick the numbers separated with comma",
            choices=choices,
        )
        for invoice in re.split(r",\s?", selected):
            invoices.append(int(invoice))
        return invoices

    @staticmethod
    def ask_invoice_discount():
        return FloatPrompt.ask(
            "[green]Please specify any discount in %", default=0.0, show_default=True
        )

    @staticmethod
    def ask_invoice_deposit_amount():
        return IntPrompt.ask(
            "[green]Please specify any deposit amount", default=0, show_default=True
        )

    @staticmethod
    def ask_invoice_deposit_vat():
        return IntPrompt.ask(
            "[green]Please specify any deposit vat", default=0, show_default=True
        )

    @staticmethod
    def ask_invoice_deposit_text():
        return Prompt.ask("Type a text for the deposit")

    @staticmethod
    def ask_line_items_confirm():
        return Confirm.ask(
            "Please confirm that these the line items that you would like to invoice",
            default=True,
        )

    @staticmethod
    def ask_invoice_confirm():
        return Confirm.ask(
            "Please confirm that this is what you would like to invoice", default=True
        )

    @staticmethod
    def ask_invoice_subject():
        return Prompt.ask("Type a subject for the invoice")

    @staticmethod
    def ask_invoice_credit(credit_days):
        return IntPrompt.ask(f"Due in: {credit_days} days?", default=30)

    @staticmethod
    def ask_invoice_confirm_their_ref(their_ref):
        return Confirm.ask(f"Their ref: {their_ref}?", default=True)

    @staticmethod
    def ask_invoice_another_their_ref():
        return Prompt.ask(f"User another Their ref")
