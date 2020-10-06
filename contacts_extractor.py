import sqlite3
import vobject


class ContactsExtractor:

    def __init__(self, conn):
        self.conn = conn

    def extract_contacts(self):
        """This method exports contacts in vcard format."""

        self.conn.row_factory = sqlite3.Row

        f = open('contacts.vcf', 'w')

        contacts = self.conn.cursor()
        contacts.execute('SELECT * FROM ABPerson ORDER BY Last, First')

        for contact in contacts:
            last = contact['Last'] if contact['Last'] is not None else ''
            first = contact['First'] if contact['First'] is not None else ''

            v_card = vobject.vCard()

            v_card.add('n')
            v_card.n.value = vobject.vcard.Name(family=last, given=first)
            v_card.add('fn')
            v_card.fn.value = first + ' ' + last

            # Get phone numbers
            phone_numbers = self.conn.cursor()
            phone_numbers.execute('SELECT label, value FROM ABMultiValue ' +
                                  'WHERE record_id=? AND property=3 ' +
                                  'ORDER BY label', (contact['ROWID'],))

            for pn in phone_numbers:
                tel = v_card.add('tel')
                tel.value = pn['value']

            phone_numbers.close()

            # Get email addresses
            email_addresses = self.conn.cursor()
            email_addresses.execute('SELECT label, value FROM ABMultiValue ' +
                                    'WHERE record_id=? AND property=4 ORDER ' +
                                    'BY label', (contact['ROWID'],))

            for ea in email_addresses:
                if ea['value'].find('@') > 2:
                    email = v_card.add('email')
                    email.value = ea['value']

            email_addresses.close()

            # Get addresses
            address_info = self.conn.cursor()
            address_info.execute('SELECT UID, value, label ' +
                                 'FROM ABMultiValue WHERE  ' +
                                 'record_id=? AND property=5 ' +
                                 'ORDER BY label', (contact['ROWID'],))
            for ai in address_info:
                value_entry = self.conn.cursor()
                value_entry.execute('SELECT key, value FROM ' +
                                    'ABMultiValueEntry WHERE parent_id=? ' +
                                    'ORDER BY key', (ai["UID"],))
                addr = {0: '', 1: '', 2: '', 3: '', 4: '', 5: ''}
                for ve in value_entry:
                    addr[ve["key"]] = ve["value"]

                a = v_card.add('adr')
                a.value = vobject.vcard.Address(
                        street=addr[1],
                        code=addr[2],
                        city=addr[3],
                        country=addr[5])

            address_info.close()

            f.write(v_card.serialize())

        # Close the file
        f.close()
        # Close the connection
        self.conn.close()
