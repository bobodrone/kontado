from rich.prompt import Prompt, Confirm, FloatPrompt


class LineItemInput:
    @staticmethod
    def ask_line_item_type():
        return Prompt.ask("[green]Which type? (service [default] or product) ")

    @staticmethod
    def ask_line_item_description():
        return Prompt.ask("[green]Please add a line item description: ")

    @staticmethod
    def ask_line_item_nth_units():
        return Prompt.ask("[green]Units (hours [default: 1], nth items) ")

    @staticmethod
    def ask_line_item_tasks(tasks):
        return Prompt.ask("[green]Task ({}) ".format(", ".join(tasks)))

    @staticmethod
    def ask_line_item_unit_price(amount, currency, type):
        return Prompt.ask(f"[green]Unit price ({amount} {currency} / {type}) ")

    @staticmethod
    def ask_line_item_vat():
        return Prompt.ask(f"[green]VAT (0, 6, 12, 25 [default]) ")

    @staticmethod
    def confirm_timer_result_time():
        return Confirm.ask(f"Is this correct? ", default=True)

    @staticmethod
    def ask_timer_result_time():
        return FloatPrompt.ask(f"Please enter the correct time (h): ")

    @staticmethod
    def confirm_git_commit():
        return Confirm.ask(f"Git commit? ", default=True)
