# coding: utf-8

from bs4 import BeautifulSoup
import re
import requests
import time
import os
import json

# TOKEN et SESSION = COOKIE À RECUP DANS BURP
TOKEN = "OWI4NjQ1N2M1MGJjNGQ3MGRiMTc4MTMyNzMxZWNhMDAyNTU1NmJiOGQ3MzQ4YmY4ZjkxNTBjNDExYjczNTM1Mg"
SESSION = "-1W3ogwpzEKQJ8UDArtg9"


COOKIES={"session": SESSION,
        "token": TOKEN
        }

# URL DE L'EVENEMENT OU DE NIMPORTE QUEL TYPE DE TICKET DE L'EVENT
URL = "https://www.ticketswap.nl/event/shelter-festimi-x-cooking-with-palms-trax-ade/84277786-1716-4f91-b073-788905efcea9"

# POUR RESERVER FAUT SADRESSER A UNE API
RESERVEURL="http://api.ticketswap.com/graphql/public/batch"

#FAIRE DU BRUIT
def beep():
    duration = 1  # seconds
    freq = 490  # Hz
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

# PARSER LES TICKETS POUR VOIR CE QUI SONT DISPO
def parseTickets(soup):

    #TOUTES LES DONNÉES SE TROUVENT DANS UNE BALISE SCRIPT. C'est ptetre pour ca que c'est un peu lent parfois
    try:
        extracted = soup.find("script", {"id": "__NEXT_DATA__"}).get_text("",strip=True)
        resJSON = json.loads(extracted)
    except error:
        print('An error occurred: '+ error)

    #REGEX DEGUEU POUR PARSER LE JSON ET TROUVER LES BILLETS QUI SONT DISPO
    tickets = resJSON['props']['pageProps']['data']['node']['types']['edges']
    for yo in tickets:
        available = yo['node']['availableTicketsCount']
        title = yo['node']['title']
        #print title
        #print available

        # ICI ON CHECK QUE LES TICKETS SONT DISPO ET ON PEUT EXCLURE CERTAINE CATÉGORIE DE TICKET. MOI J'AI EXCLU CEUX OU YA ECRIT SHUTTLEBUS /!\ CASE SENSITIVE
        if available != '0' and available and "Shuttlebus" not in title:
            print (title)
            yoyo = yo['node']['availableListings']['edges']
            for we in yoyo:

                #RECUP TOKEN ET ID DU TICKET QUI SONT LES DEUX INFOS NECESSAIRES POUR LE RESERVER
                token = we['node']['id']
                path = we['node']['uri']['path'].split("/")
                Id = path[4].split('?')[0]
                #print Id
                #print token
                reserveTicket(Id,token)
                #beep()
                break


def reserveTicket(Id,token):

    # HEADER A FOURNIR
    header={'Authorization': 'Bearer ' + TOKEN}

    # LES PARAMETRES POST SONT JSON, FAUT DONC LES SOUMETTRE COMME SUIT AVEC json=data au moment de la requete post
    data = [{"operationName":"addTicketsToCart","variables":{"input":{"listingId":token,"listingHash":Id,"amountOfTickets":1}},"query":"mutation addTicketsToCart($input: AddTicketsToCartInput!) {\n  addTicketsToCart(input: $input) {\n    cart {\n      id\n      __typename\n    }\n    errors {\n      code\n      message\n      __typename\n    }\n    __typename\n  }\n}\n"}]

    req = requests.post(RESERVEURL, headers=header, json=data)
    rep = req.text
    print (rep)

    # SI YA PAS EU D'ERREUR SEND SMS
    if "NoTicketsCouldBeReservedError" not in rep:
        beep()
        sendSMS()


def sendSMS():
    print("U got a tickettttt")

def main():
    s = requests.Session()
    bar = "=>"
    i = 0
    while True:
        r = s.get(URL,cookies=COOKIES)
        soup = BeautifulSoup(r.text,features="html.parser")
        parseTickets(soup)
        # Display Bar
        if i < 100:
            print(bar)
            bar = bar[:-1]+"=>"
            i+=1
        else:
            bar = "=>"
            i = 0
            print(bar)

        #SLEEP POUR EVITER QUE CE SOIT TROP RALENTIT
        time.sleep(1)

if __name__ == "__main__":
    main()

