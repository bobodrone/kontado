# kontado
Terminal based time reporting and invoicing system written in Python

## Install

kontado is built with Python 3.12 and uses [Poetry](https://python-poetry.org/)
for dependency management.

### 1. Prerequisites

- Python `3.12` (see `.tool-versions`, e.g. 3.12.9)
- [Poetry](https://python-poetry.org/docs/#installation)
- `wkhtmltopdf` is required by the PDF generation step (the `invoice pdf`
  command). Install it through your package manager, e.g.:

  ```bash
  # Debian / Ubuntu
  sudo apt install wkhtmltopdf

  # macOS (Homebrew)
  brew install wkhtmltopdf
  ```

### 2. Clone the repository

```bash
git clone https://github.com/<your-org>/kontado.git
cd kontado
```

### 3. Create a virtual environment and install dependencies with Poetry

```bash
# Configure Poetry to create the virtualenv inside the project folder
poetry config virtualenvs.in-project true

# Create the virtual environment (using the Python 3.12 from .tool-versions)
poetry env use 3.12

# Install all dependencies from pyproject.toml / poetry.lock
poetry install

# Activate the virtual environment for the following commands
poetry shell
```

From now on every `python cli.py ...` command below is expected to be run
from the repository root while the virtual environment is active. Inside the
Poetry shell this means:

```bash
python cli.py --help
```

The CLI is built with [typer](https://typer.tiangolo.com/), so every command
accepts `--help` to list its subcommands and options.

## Initialize a kontado project

`init` creates a new kontado project folder (by default called `kontado`) in the
current directory. The folder holds the `config/` and `clients/` directories as
well as a `.kontado` marker file that the other commands look for.

```bash
python cli.py init
```

You will be prompted for:

- the folder name to create (default `kontado`)
- confirmation to create the folder
- whether to initialize a GIT repository inside the new folder (recommended)

A kontado project must exist before any other command can run, since they
search the current directory and its parents for the `.kontado` marker file.
Run the rest of the commands from inside the newly created kontado folder:

```bash
cd kontado
```

## Create one or more clients

Clients are stored under `clients/<client-name>/`. Each client has its own
config and a collection of projects.

```bash
python cli.py client create
```

The prompt asks for:

- a machine name for the client (used as the folder name, e.g. `acme`)
- a full/label name (e.g. `Acme Corporation`)
- confirmation before the client is created

Repeat the command for as many clients as you need. List or inspect existing
clients with:

```bash
python cli.py client list
python cli.py client show            # interactive selection
python cli.py client show acme       # show a specific client directly
```

## Create one or more projects per client

A project always belongs to a client. When you create a project you first pick
the parent client from a numbered list, then provide project details.

```bash
python cli.py project create
```

You will be prompted to:

1. select the client (choose a number from the listed clients)
2. enter a project machine name (used as the project folder name)
3. enter a project label / full name
4. enter an optional description
5. confirm the creation

Run the command again to add more projects to the same or another client. List
or inspect projects with:

```bash
python cli.py project list
python cli.py project show
```

## Report time

There are two ways to register time, both resulting in a line item created under
`clients/<client>/projects/<project>/line_items/`:

### Option A: use the built-in timer

The timer tracks a running session and converts it into a line item when
stopped.

```bash
# Start a timer (you select client, project and task interactively)
python cli.py timer start

# Check whether a timer is running and for how long
python cli.py timer status

# Stop the running timer and create the corresponding line item.
# You will be asked to confirm/adjust the rounded hours, add a description,
# and optionally create a git commit for the saved line item file.
python cli.py timer stop
```

### Option B: register time directly as a line item

Use this when you already know the hours to report and don't need a live
timer. The command walks you through client, project and task selection and
then asks for description, units (`nth`, e.g. hours), unit price, task, VAT and
currency.

```bash
python cli.py time create
```

> Note: in `cli.py` the line item command group is registered as `time`, so the
> command above is `python cli.py time create` (see `cli.py:43-47`).

There is also an `import` subcommand that loads line items from a CSV file:

```bash
python cli.py time import /path/to/line_items.csv
```

## Generate invoices from the reported time

Once you have un-invoiced line items you can create an invoice. The CLI groups
the line items per selected project and computes netto and VAT sums.

```bash
python cli.py invoice create
```

The interactive flow:

1. Optionally enter freeform mode (create ad-hoc line items directly during
   invoice creation) by answering the first prompt.
2. Select the client.
3. Select one or more projects whose un-invoiced line items should be
   included.
4. Review the collected line items and confirm.
5. Optionally apply a discount (percentage) and a deposit amount.
6. Confirm the totals, then provide a subject, credit days and a reference for
   the recipient (`their_ref`).

The created invoice is stored under `clients/<client>/invoices/`.

Useful related commands:

```bash
# Preview the un-invoiced line items grouped by project/service/price
python cli.py invoice uninvoiced

# List invoices (optionally filter by status: created, sent, paid)
python cli.py invoice list
python cli.py invoice list --status sent

# Mark invoices as sent
python cli.py invoice sent

# Mark invoices as paid
python cli.py invoice paid

# Roll back (revert) an invoice
python cli.py invoice rollback
```

## Generate a PDF from an invoice

The `invoice pdf` command renders a previously created invoice to a PDF file.
It depends on `wkhtmltopdf` (see the Install section).

```bash
python cli.py invoice pdf
```

You will be prompted to:

1. select the client
2. select the invoice (by invoice number) from the listed invoices

The PDF is then generated by `InvoiceService.generate(...)` and written next
to the invoice data (see `main/commands/invoice.py:386-413`).

## Command overview

| Command                       | Description                                              |
| ----------------------------- | -------------------------------------------------------- |
| `python cli.py init`          | Initialize a new kontado project folder                  |
| `python cli.py client create` | Create a client                                          |
| `python cli.py client list`   | List clients                                             |
| `python cli.py client show`   | Show one or all clients                                  |
| `python cli.py project create`| Create a project for a client                            |
| `python cli.py project list`  | List projects for a client                               |
| `python cli.py project show`  | Show project details                                     |
| `python cli.py timer start`   | Start the running timer                                  |
| `python cli.py timer status`  | Show the running timer status                            |
| `python cli.py timer stop`    | Stop the timer and create a line item                    |
| `python cli.py time create`   | Manually create a line item (time reporting)             |
| `python cli.py time import`   | Import line items from a CSV file                        |
| `python cli.py invoice create`| Create an invoice from un-invoiced line items            |
| `python cli.py invoice uninvoiced` | Preview un-invoiced line items                      |
| `python cli.py invoice list`  | List invoices (filter with `--status created/sent/paid`)|
| `python cli.py invoice sent`  | Mark invoices as sent                                    |
| `python cli.py invoice paid`  | Mark invoices as paid                                    |
| `python cli.py invoice pdf`   | Generate a PDF from an existing invoice                  |
| `python cli.py invoice rollback` | Roll back (revert) an invoice                        |

Every command supports `--help`, e.g. `python cli.py invoice create --help`.

## Run application

```bash
python cli.py [command] [args]
```