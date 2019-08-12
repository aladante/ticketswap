# coding: utf-8

from twilio.rest import Client
from bs4 import BeautifulSoup
import re
import requests
import time
import os
import json

# TOKEN et SESSION = COOKIE À RECUP DANS BURP
TOKEN = "A_REMPLIR"
SESSION = "A_REMPLIR"

COOKIES={"session": SESSION,
        "token": TOKEN
        }

# URL DE L'EVENEMENT OU DE NIMPORTE QUEL TYPE DE TICKET DE L'EVENT
URL = "https://www.ticketswap.com/event/waking-life-2019/regular/f3daf6fc-3966-4277-b8be-a982478dfa24/1089959"

# POUR RESERVER FAUT SADRESSER A UNE API
RESERVEURL="http://api.ticketswap.com/graphql/public/batch"

# TWILIO ACCESS POUR ENVOYER SMS
ACCOUNT_SID = "A_REMPLIR"
AUTH_TOKEN = "A_REMPLIR"

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
    tickets = resJSON['props']['pageProps']['data']['node']['event']['types']['edges']
    for yo in tickets:
        available = yo['node']['availableTicketsCount']
        title = yo['node']['title']
        #print title
        #print available

        # ICI ON CHECK QUE LES TICKETS SONT DISPO ET ON PEUT EXCLURE CERTAINE CATÉGORIE DE TICKET. MOI J'AI EXCLU CEUX OU YA ECRIT SHUTTLEBUS /!\ CASE SENSITIVE
        if available != '0' and available and "Shuttlebus" not in title:    
            print title
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
    print rep
    
    # SI YA PAS EU D'ERREUR SEND SMS
    if "NoTicketsCouldBeReservedError" not in rep:
        beep()
        sendSMS()


def sendSMS():
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
    to="NUM_DESTINATAIRE",
    from_="NUM_TWILIO",
    body="WEWEWE C BUEN"
    )

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

