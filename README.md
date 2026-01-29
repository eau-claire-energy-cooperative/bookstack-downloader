# BookStack Downloader
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg)](https://github.com/RichardLitt/standard-readme)

Quickly export books, chapters, or pages from a [BookStack](https://www.bookstackapp.com) site for offline archiving.

## Install

Cloning and installing this repository will enable access to the `bookstack-downloader` tool via the command line. It is recommended to run this in a Python virtual environment.

```

# clone the repository
git clone https://github.com/eau-claire-energy-cooperative/bookstack-downloader

# create the virtual environment
python3 -m venv .venv

# activate and install dependencies
source .venv/bin/activate

# install the downloader
pip3 install .

```

### Development

If installing for development usage, edit the final installation line to allow for interactive editing of the source files.

```

pip3 install -e ".[dev]"

```

## Usage

Once installed you can use the tool `bookstack-downloader` from the command line. Before you can connect to a BookStack instance you will need to generate a token ID and secret. You can find how to get these values from your BookStack instance's doc page at `http[s]://<example.com>/api/docs`.

Run the tool with `-h` to see all the available command line options.

```
usage: bookstack-downloader [-h] [-c CONFIG] -u URL -T TOKEN -S SECRET [-d DIRECTORY] (-s SHELF | -b BOOK) [--dir-clear | --modified-only] [--split-book] [--test]

BookStack Downloader

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to custom config file

Authentication:
  -u URL, --url URL     base URL of the BookStack instance
  -T TOKEN, --token TOKEN
                        authorization token
  -S SECRET, --secret SECRET
                        authorization secret

Download Settings:
  -d DIRECTORY, --directory DIRECTORY
                        directory to download PDFs, default is downloads
  -s SHELF, --shelf SHELF
                        The slugified version of a shelf to export
  -b BOOK, --book BOOK  The slugged version of a book to export
  --dir-clear           Clears the downloads directory before export
  --modified-only       Only download if books/chapters/pages changed since last run
  --split-book          Split the book into separate chapter/page PDFs instead of one big file
  --test                Runs in test mode, will not download or modify any files
```

### Config File

For ease of use, arguments can be put in a config file with the format `arg=value`, one per line. Pass in the path to the config file with the `-c` option.

### Downloading Books

Books are downloaded by into PDF files. You pass in the slugified name of either a shelf (`-s`) or a single book (`-b`). These can be found in the URL for the object. As an example, if the shelf is called "Library Books" the slugified version is "library-books". By default each book will download to a single PDF file with all the chapters and pages. If you want to split up the contents even more the `--split-book` option will create a folder for the book and download each chapter or page to it's own PDF file.

### Downloading Modified Only

It is possible to only download content that has changed since the last run of the script. To do this use the `--modified-only` flag. When this is turned on, the first time run all content will be downloaded. You'll notice a text file in the downloads directory called `last_run.txt`. This contains the date/time of the last run of the script. On the next run this date will be used to compare the updated date for all books, chapters, and pages selected for download. Only those that have been updated since the last run will be downloaded.

__Note:__ That if a single page within a book is updated, the entire book will be downloaded. This is true even if `--split-book` is being used.

## Contributing

This is an internal tool posted in the hopes it will help someone with a similar issue. Post an [Issue](https://github.com/eau-claire-energy-cooperative/bookstack-downloader/issues) for errors with base functionality but no enhancements beyond what we need for our use cases will be considered.

## License

[GPLv3](/LICENSE)
