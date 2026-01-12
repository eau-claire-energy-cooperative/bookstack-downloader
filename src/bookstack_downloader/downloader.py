import configargparse
import bookstack

def main():
    parser = configargparse.ArgumentParser(description='BookStack Downloader')
    parser.add_argument('-c', '--config', is_config_file=True, help='Path to custom config file')
    parser.add_argument('-u', '--url', required=True, help='base URL of the BookStack instance')
    parser.add_argument('-T', '--token', required=True, help='authorization token')
    parser.add_argument('-S', '--secret', required=True, help='authorization secret')
    args = parser.parse_args()

    # try and connect to the api
    api = bookstack.BookStack(args.url, token_id=args.token, token_secret=args.secret)

    # need to generate these or it won't work
    api.generate_api_methods()

    print(api.get_system_read())

if __name__ == '__main__':
    main()
