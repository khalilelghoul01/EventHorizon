import argparse


def handleArgs():
    parser = argparse.ArgumentParser(description='Handle Senarios.')
    parser.add_argument('senarios', metavar='senarios', type=str,
                        help='The path of the senarios.')
    parser.add_argument('--browser', nargs='?', dest='browser', type=str,
                        help='The browser to use.')
    parser.add_argument('--report', nargs='?', dest='report', type=str,
                        help='The report path.')
    parser.add_argument('--remote', nargs='?', dest='remote', type=str,
                        help='The remote server.')
    parser.add_argument('--maximize', action='store_true',
                        help='maximize the browser window.')
    parser.add_argument('--headless',  action='store_true',
                        help='The remote server.')
    args = parser.parse_args()
    return {
        'scenarios': args.senarios,
        'browser': args.browser,
        'report': args.report,
        'remote': args.remote,
        'maximize': args.maximize,
        'headless': args.headless
    }
