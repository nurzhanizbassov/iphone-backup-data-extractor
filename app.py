#!./venv/bin/python
import sqlite3
import os
import argparse
from sqlite3 import Error
from contacts_extractor import ContactsExtractor
from constants import ADDRESS_BOOK_PATH, MAIN_DB


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('path', type=dir_path)

    parser.add_argument(
        '-c', '--contacts',
        action='store_true',
        help=(
            'Extract contacts from '
            'the itunes backup'
        )
    )
    # TODO: Add whatsapp data extraction
    parser.add_argument(
        '-w', '--whatsapp',
        action='store_true',
        help=(
            'Extract whatsapp data '
            'from the itunes backup. '
            'Not implemented yet.'
        )
    )

    args = parser.parse_args()

    if args.contacts:
        extract_contacts(args)
    elif args.whatsapp:
        print('This feature has not been implemented yet')


def extract_contacts(args):
    conn = create_connection(args.path + '/' + MAIN_DB)
    file_id = find_contacts_db_hash(conn)
    contacts_file = find_file_by_hash(file_id, args.path)
    conn = create_connection(contacts_file)
    _contacts_extractor = ContactsExtractor(conn)
    _contacts_extractor.extract_contacts()
    print('Contacts have been extracted into contacts.vcf')


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(
            f'readable_dir:{path} is not a valid path'
        )


def find_contacts_db_hash(conn):
    """
    Query all rows in the Files table
    of the Manifest.db
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(
            'SELECT fileID '
            'FROM Files where relativePath LIKE "%{}%"'
            .format(ADDRESS_BOOK_PATH)
            )
    row = cur.fetchone()
    file_id = row[0]
    cur.close()
    conn.close()
    return file_id


def find_file_by_hash(file_id, backup_path):
    for root, dirs, files in os.walk(backup_path):
        for file in files:
            if file == file_id:
                return (os.path.join(root, file))
    return None


def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


if __name__ == "__main__":
    main()
