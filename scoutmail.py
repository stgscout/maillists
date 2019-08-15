"""Filter csv list from scoutnet and extract all email addresses for members.

Generate one import list for G-Suite for each 'avdelning'.
"""


from argparse import ArgumentParser

LIST_MAP = {'Stimmet': 'stimmet@stgscout.se',
            'Flocken': 'flocken@stgscout.se',
            'Konvojen-Babord': 'babord@stgscout.se',
            'Konvojen-Styrbord': 'styrbord@stgscout.se',
            'Primusgastarna-Nord': 'nord@stgscout.se',
            'Primusgastarna-Syd': 'syd@stgscout.se',
            'Drakdräparna': 'drakdraparna@stgscout.se',
            'Rover': 'rover@stgscout.se'}


def csv_split(infile):
    "Generator which return a list for each CSV line."
    with open(infile) as ifh:
        data = ifh.read()
    parts = []
    inside = False
    part = ""
    for c in data:
        if c == '"':
            inside = not inside
        if not inside:
            if c == '"':
                parts.append(part)
                part = ""
            elif c == '\n':
                yield parts
                parts = []
        elif c != '"':
            part += c
    if len(parts) > 0:  # If no newline at end
        return parts

def main():

        email_lists = {}  # Elements are [email]
        avdelnings_col_nr = 0

        parser = ArgumentParser()
        parser.add_argument('infile')
        args = parser.parse_args()

        csv_len = None
        line_nr = 0
        for parts in csv_split(args.infile):
            if csv_len is None:
                csv_len = len(parts)
                assert len(parts) == csv_len
            if line_nr == 0:
                for col_nr, p in enumerate(parts):
                    if p == "Avdelning": #Här blev det ett komma med!
                        avdelnings_col_nr = col_nr
                        line_nr = 1
                        break
            else:  # line_nr > 0
                if csv_len < avdelnings_col_nr + 1:
                    continue
                avdelning = parts[avdelnings_col_nr]
                if avdelning == "":
                    continue
                if not avdelning in email_lists:
                    email_lists[avdelning] = set()
                for p in parts:
                    if p.find('@') >= 0:
                        email_lists[avdelning].add(p)

        for avdelning, emails in email_lists.items():
            lista = LIST_MAP.get(avdelning)
            if lista is not None:
                with open(avdelning + '.csv', 'w') as ofh:
                    ofh.write('Group Email,Member Email,Member Type,Member Role\n')
                    emails = list(emails)
                    # emails.append(f'{lista}')
                    emails.sort()

                    for email in emails:
                        if email == f'{lista}':
                            ofh.write(f'{lista},{email},GROUP,OWNER\n')
                        else:
                            ofh.write(f'{lista},{email},USER,MEMBER\n')


if __name__ == "__main__":
    main()
