import bookstack
import configargparse
import os
import os.path
import shutil


class Downloader:
    api = None
    download_dir = "downloads"

    def __init__(self, url, token, secret, download_dir):
        self.api = bookstack.BookStack(url, token_id=token, token_secret=secret)
        self.download_dir = download_dir

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

    def export_book(self, book_id, split_book):

        # load detailed information on this book
        book_info = self.api.get_books_read({'id': book_id})
        print(f"Extracting {book_info['name']}")

        if (not split_book):
            # download the entire book
            pdf = self.api.get_books_export_pdf({"id": book_id})
            self._write_file(pdf, f"{os.path.join(self.download_dir, book_info['name'])}.pdf")

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

        print(f"Connected to {info['app_name']} version {info['version']}")


def create_folder(path):
    if (not os.path.exists(path)):
        os.makedirs(path)
    return path


def main():
    parser = configargparse.ArgumentParser(description='BookStack Downloader')
    parser.add_argument('-c', '--config', is_config_file=True, help='Path to custom config file')

    # authentication arguments
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument('-u', '--url', required=True, help='base URL of the BookStack instance')
    auth_group.add_argument('-T', '--token', required=True, help='authorization token')
    auth_group.add_argument('-S', '--secret', required=True, help='authorization secret')

    # configuration argu8ments
    config_group = parser.add_argument_group("Download Settings")
    config_group.add_argument('-d', '--directory', required=False, default="downloads", help="directory to download PDFs, default is %(default)s")

    mutually_ex = config_group.add_mutually_exclusive_group(required=True)
    mutually_ex.add_argument('-s', '--shelf', help="The slugified version of a shelf to export")
    mutually_ex.add_argument('-b', '--book', help="The slugged version of a book to export")

    config_group.add_argument('--split-book', action='store_true', help='Split the book into separate chapter/page PDFs instead of one big file')
    config_group.add_argument('--dir-clear', action='store_true', help="Clears the downloads directory before export")

    args = parser.parse_args()

    if (args.dir_clear):
        print(f"Clearing {args.directory} before export")
        if (os.path.exists(args.directory)):
            shutil.rmtree(args.directory)

    # create the downloads directory
    create_folder(args.directory)

    # try and connect to the api
    downloader = Downloader(args.url, args.token, args.secret, args.directory)
    downloader.print_system_info()

    if (args.shelf):
        # try and find the shelf
        shelf = downloader.get_shelf(args.shelf)

        if (shelf is not None):
            if (len(shelf['books']) > 0):
                print(f"{shelf['name']} has {len(shelf['books'])} books")

                for b in shelf['books']:
                    downloader.export_book(b['id'], args.split_book)
            else:
                print(f"{shelf['name']} does not have books to export")
    else:
        # try and find this book
        book = downloader.get_book(args.book)

        if (book is not None):
            # download this book
            downloader.export_book(book['id'], args.split_book)
        else:
            print(f"{args.book} is not a valid book")


if __name__ == '__main__':
    main()
