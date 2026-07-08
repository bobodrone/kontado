from .formatters import TableFormatter


class ProjectListTableFormatter(TableFormatter):
    def format_table(self, data):
        self.table.add_column("No", style="cyan")
        self.table.add_column("Project")
        self.table.add_column("Name")
        self.table.add_column("Description")

        index = 0
        for project in data:
            index = index + 1
            self.table.add_row(
                f"{index}",
                project.label,
                project.name,
                project.description,
            )


class TasksListTableFormatter(TableFormatter):
    def format_table(self, data):
        self.table.add_column("Task", style="cyan")
        self.table.add_column("Description")
        self.table.add_column("Debit info")
        self.table.add_column("VAT Info")
        self.table.add_column("Default")

        index = 0
        for task in data:
            index = index + 1
            if task.rate.amount and task.rate.currency and task.rate.type:
                debit = f"{task.rate.amount / 100: {'8,.2f'}} {task.rate.currency} / {task.rate.type}"
            else:
                debit = ""
            self.table.add_row(
                f"{index}",
                f"{task.label} ({task.type})",
                debit,
                f"{task.rate.vat} %" if task.rate.vat else "",
                "X" if task.default else "",
            )


class ProjectTableFormatter(TableFormatter):
    def format_table(self, data):
        self.table.add_column("Client")
        self.table.add_column("Project")
        self.table.add_column("Tasks")

        rows = []
        for task in data.tasks:
            task_parts = [f"{task.label} ({task.type})"]
            if task.default:
                task_parts.append(f"Default: {task.default}")
            task_parts.append(f"Rate: {task.rate.amount // 100} {task.rate.currency}/h")
            task_parts.append(f"VAT: {task.rate.vat}%")
            task_parts.append("")
            rows.append("\n".join(task_parts))

        self.table.add_row(
            data.client,
            f"{data.label} ({data.name})\n{data.description}",
            "\n".join(rows),
        )
