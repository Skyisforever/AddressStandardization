from pymongo import MongoClient
import sys
import nltk
from fuzzywuzzy import fuzz, process
from nltk.tokenize.treebank import TreebankWordDetokenizer
import re


def run(s):

    client = MongoClient()
    db = client.maps

    address = s

    address = address.upper()
    pretokens = nltk.word_tokenize(address.upper())
    extra=False
    tokens=[]
    street_type=False
    street_types = {"LANE":"LN", "DRIVE":"DR", "COURT":"CT", "ROAD":"RD", "STREET":"ST", "AVENUE":"AVE", "TERRACE":"TER", "TERR":"TER", "BOULEVARD":"BLVD", "BOUL":"BLVD", "BOULV":"BLVD"}
    for i in pretokens:
        if re.match("^\d{5}-\d{4}$", i):
            main, extra = i.split('-')
            tokens.append(main)
        elif i in street_types:
            street_type = street_types[i]
        elif i in street_types.values():
            street_type = i
        tokens.append(i)

    address = re.sub("(\d{5})-\d{4}", r"\1", address)
    numbers = filter(str.isdigit, tokens)
    if not numbers:
        return "No results found"

    ini_filtered = db.addresses.find({"number": numbers[0]} if len(numbers)==1 else {"number":numbers[0], "zipcode":numbers[1]})

    m = 0
    ob = None
    for i in ini_filtered:
        if i['zipcode']==u" " or i['zipcode']==u"":
            continue
        x = " ".join(i.values()[:4]+i.values()[5:-2])
        tokens = nltk.word_tokenize(x)
        score = fuzz.token_set_ratio(address, x)
        if street_type and (street_type in tokens or ("AV" in tokens and street_type=="AVE")):
            score *= 1.15
        if score > m:
            m = score
            ob = i


    if ob==None:
        print "No results found at all"
        return "No results found at all"
       # sys.exit(0)

    if score<20:
        print "No results found"
        return "No results found"
        #sys.exit(0)

    trans = {"av": "ave"}
    uppers = ["NW", "SW", "SE", "NE"]
    street = TreebankWordDetokenizer().detokenize(trans[i.lower()].title() if i.lower() in trans else (i.upper() if i.upper() in uppers else i.title()) for i in nltk.word_tokenize(ob['street']))

    city = ob['city'] if ob['city'] else db.zips.find_one({"zipcode": ob['zipcode']})['city']

    standard = ob['number'] + " " + street + " " + city.title() + " " + ob['state'].upper() + " " + ob['zipcode']+("-"+extra if extra else "")

    print standard
    return standard
