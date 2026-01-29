import bookstack
import configargparse
import datetime
import os
import os.path
import shutil
import time


LAST_RUN_FILE = 'last_run.txt'


class Downloader:
    api = None
    download_dir = "downloads"
    test_mode = False

    def __init__(self, url, token, secret, download_dir, test_mode=False):
        self.api = bookstack.BookStack(url, token_id=token, token_secret=secret)
        self.download_dir = download_dir
        self.test_mode = test_mode

        # generate these at the start or it won't work
        self.api.generate_api_methods()

    def _write_file(self, pdf_contents, path):
        with open(path, "wb") as binary_file:
            binary_file.write(pdf_contents)

    def _load_shelves(self):
        result = {}

        shelves = self.api.get_shelves_list()

        # get name/id pairs
        for s in shelves['data']:
            result[s['slug']] = s['id']

        return result

    def _create_date(self, date_str):
        # ISO 8601 with Z for UTC, Python < 3.11 has trouble so strip Z and add TZ offset
        return datetime.datetime.fromisoformat(f"{date_str[:-1]}+00:00")

    """
    iterates through item and checks updated date of parent and all children
    return True if any have been modified since updated_since or if updated_since is None
    """
    def _check_modified(self, item, updated_since, key='contents'):
        result = False  # assume item has not been modified

        if (updated_since is not None):
            # check book level to see if anything has been modified
            if (self._create_date(item['updated_at']) >= updated_since):
                result = True
            else:
                # check all items in the book
                for i in item[key]:
                    # if chapter recurse through pages
                    if ('type' in i and i['type'] == 'chapter' and self._check_modified(i, updated_since, 'pages')):
                        result = True
                    elif (self._create_date(i['updated_at']) >= updated_since):
                        print(f"Page {i['name']} modified {i['updated_at']}")
                        result = True
        else:
            # don't care about modified date, download anyway
            result = True

        return result

    def export_book(self, book_id, updated_since, split_book):

        # load detailed information on this book
        book_info = self.api.get_books_read({'id': book_id})

        # check if this book should be downloaded
        should_download = self._check_modified(book_info, updated_since)

        if (should_download):
            print(f"Extracting {book_info['name']}")

            if (not split_book and not self.test_mode):
                # download the entire book
                pdf = self.api.get_books_export_pdf({"id": book_id})
                self._write_file(pdf, f"{os.path.join(self.download_dir, book_info['name'])}.pdf")

            else:
                if (self.test_mode):
                    for item in book_info['contents']:
                        print(f"Saving {item['name']}: {item['type']}")
                else:
                    # create a download path specific to this book
                    path = create_folder(f"{self.download_dir}/{book_info['name']}")

                    # for each chapter/page in the book, download it
                    for item in book_info['contents']:
                        print(f"Saving {item['name']}: {item['type']}")

                        if (item['type'] == 'chapter'):
                            pdf = self.api.get_chapters_export_pdf({"id": item['id']})
                        elif (item['type'] == 'page'):
                            pdf = self.api.get_pages_export_pdf({"id": item['id']})
                        self._write_file(pdf, f"{os.path.join(path, item['name'])}.pdf")

    def get_shelf(self, shelf_name):
        result = None
        shelves = self._load_shelves()

        if (shelf_name in shelves):
            result = self.api.get_shelves_read({"id": shelves[shelf_name]})
        else:
            print(f"{shelf_name} is not a valid shelf")

        return result

    def get_book(self, book_name):
        result = None

        books = self.api.get_books_list()

        for b in books['data']:
            if (b['slug'] == book_name):
                result = b
                break

        return result

    def print_system_info(self):
        info = self.api.get_system_read()

        if (self.test_mode):
            print("Running in TEST MODE - no files will be modified")

        print(f"Connected to {info['app_name']} version {info['version']}")


def create_folder(path):
    if (not os.path.exists(path)):
        os.makedirs(path)
    return path


def read_last_run(path):
    result = None

    # read in the last run time, if it exists
    if (os.path.exists(os.path.join(path, LAST_RUN_FILE))):
        with open(os.path.join(path, LAST_RUN_FILE), 'r') as last_run_file:
            # bookstack stores in UTC time
            result = datetime.datetime.fromtimestamp(float(last_run_file.read()), tz=datetime.timezone.utc)
    else:
        # create the earliest possible date
        result = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.timezone.utc)
        print(result)

    return result


def write_last_run(path):
    # set the last run time to now
    with open(os.path.join(path, LAST_RUN_FILE), "w") as last_run_file:
        last_run_file.write(f"{time.time()}")


def main():
    parser = configargparse.ArgumentParser(description='BookStack Downloader')
    parser.add_argument('-c', '--config', is_config_file=True, help='Path to custom config file')

    # authentication arguments
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument('-u', '--url', required=True, help='base URL of the BookStack instance')
    auth_group.add_argument('-T', '--token', required=True, help='authorization token')
    auth_group.add_argument('-S', '--secret', required=True, help='authorization secret')

    # configuration arguments
    config_group = parser.add_argument_group("Download Settings")
    config_group.add_argument('-d', '--directory', required=False, default="downloads", help="directory to download PDFs, default is %(default)s")

    mutually_ex1 = config_group.add_mutually_exclusive_group(required=True)
    mutually_ex1.add_argument('-s', '--shelf', help="The slugified version of a shelf to export")
    mutually_ex1.add_argument('-b', '--book', help="The slugged version of a book to export")

    mutually_ex2 = config_group.add_mutually_exclusive_group(required=False)
    mutually_ex2.add_argument('--dir-clear', action='store_true', help="Clears the downloads directory before export")
    mutually_ex2.add_argument('--modified-only', action='store_true', help="Only download if books/chapters/pages changed since last run")

    config_group.add_argument('--split-book', action='store_true', help='Split the book into separate chapter/page PDFs instead of one big file')
    config_group.add_argument('--test', action="store_true", help="Runs in test mode, will not actually download PDF files")

    args = parser.parse_args()

    if (args.dir_clear and not args.test):
        print(f"Clearing {args.directory} before export")
        if (os.path.exists(args.directory)):
            shutil.rmtree(args.directory)

    # create the downloads directory
    create_folder(args.directory)

    # try and connect to the api
    downloader = Downloader(args.url, args.token, args.secret, args.directory, args.test)
    downloader.print_system_info()

    last_run = None
    if (args.modified_only):
        last_run = read_last_run(args.directory)
        print(f"Downloading information modified since {last_run}")

    success = not args.test  # don't write files in test mode
    if (args.shelf):
        # try and find the shelf
        shelf = downloader.get_shelf(args.shelf)

        if (shelf is not None):
            if (len(shelf['books']) > 0):
                print(f"{shelf['name']} has {len(shelf['books'])} books")

                for b in shelf['books']:
                    downloader.export_book(b['id'], last_run, args.split_book)
            else:
                success = False
                print(f"{shelf['name']} does not have books to export")
    else:
        # try and find this book
        book = downloader.get_book(args.book)

        if (book is not None):
            # download this book
            downloader.export_book(book['id'], last_run, args.split_book)
        else:
            success = False
            print(f"{args.book} is not a valid book")

    if (success and args.modified_only):
        write_last_run(args.directory)


if __name__ == '__main__':
    main()
