#!/usr/bin/env python3

import card_me
from config import config


def make_card(person):
    first = person['name'].split()[0]
    last = person['name'].split()[1:]
    card = card_me.vCard()

    # Name
    card.add('n')
    card.n.value = card_me.vcard.Name(family=last, given=first)

    card.add('fn')
    card.fn.value = person['name']

    # E-mail
    card.add('email')
    card.email.value = person['email']
    card.email.type_param = 'INTERNET'
    return card


# Make vcard for Lab Tas
people = []
for ta in config['admin']['lab_TAs'].values():
    people += ta

vcard_f = open("csc161-tas.vcard", 'w')

for person in people:
    if not person['name']:
        continue

    card = make_card(person)
    vcard_f.write(card.serialize())

vcard_f.close()

# Make vcard for workshop leaders
people = config['admin']['workshop_leaders'].values()
vcard_f = open("csc161-wsl.vcard", 'w')

for person in people:
    if not person['name']:
        continue

    card = make_card(person)
    vcard_f.write(card.serialize())

vcard_f.close()
