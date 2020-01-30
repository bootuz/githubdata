import json
from datetime import datetime


def date_formatter(date):
    f_date = datetime.strptime(date, '%d-%m-%Y')
    return f_date.strftime('%Y-%m-%d')


def print_like_table(data):
    # with open(file_path, 'r') as file:
    #     data = json.load(file)

    most_contribs = list({k: v for k, v in sorted(data.items(), reverse=True, key=lambda item: item[1])}.items())[:30]
    tab = len(max(most_contribs, key=lambda x: len(x[0]))[0])

    header = f'Login{" " * tab}| Num. of commits'
    print(header)
    print('-' * len(header))

    for k, v in most_contribs:
        print(f'{k}{" " * (tab - len(k) + 5)}| {v}')
    print('-' * len(header))

