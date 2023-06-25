import telegram
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Updater
from bs4 import BeautifulSoup
import requests
import schedule
import time

# Token del tuo bot Telegram
TOKEN = 'Inserisci il Token' #Ottienilo da @Bot_Father

# URL della pagina web delle offerte, sostituisci citta' e categoria di prodotto con la tua preferenza
URL = 'https://www.doveconviene.it/roma/prodotti/energy-drink'

# ID delle chat degli utenti a cui inviare le notifiche (facoltativo)
#user_ids = [ID, ID, ID]  # Sostituisci con gli ID dei chat degli utenti, rimuovi '#' all'inizio

# Funzione per effettuare lo scraping delle offerte dalla pagina web fornita
def scrape_offers():
    response = requests.get(URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        offers = []
		# Scraping per trovare il venditore, prodotto e prezzo
        retailer_tags = soup.find_all('h3', class_='product__retailer-name font--bold')
        product_tags = soup.find_all('h2', class_='product__name font--bold')
        price_tags = soup.find_all('h4', class_='product__price-extended color--primary font--bold')
		
		# Verrà selezionato qualsiasi prodotto che abbia nel campo di testo il nome del prodotto
        for retailer_tag, product_tag, price_tag in zip(retailer_tags, product_tags, price_tags):
            retailer = retailer_tag.text.strip()
            product = product_tag.text.strip()
            price = price_tag.find('span', class_='digits').text.strip()
            if 'monster' in product.lower():
                offers.append({'retailer': retailer, 'product': product, 'price': price})

        return offers

# Funzione per la ricerca delle offerte (puoi mostrare all'utente la lista con il comando configurandolo da @Bot_Father)
def monster_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Elaboro le offerte...")
	# Richiama la funzione di scraping della pagina web
    offers = scrape_offers()
    if offers:
        message = "Sono disponibili le seguenti offerte nella tua zona:\n\n"
        for offer in offers:
            message += f"{offer['retailer']}, {offer['product']} a {offer['price']} euro\n"

        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
	# Se non viene trovata nessuna offerta manderà all'utente il seguente messaggio
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Nessuna offerta trovata.")

# Funzione Main del bot con le dichiarazioni base per il corretto funzionamento
def main():
    global bot
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(bot=bot,request_kwargs={'proxy_url': 'socks5://127.0.0.1:1080'})
    dispatcher = updater.dispatcher

    # Registra lo scheduling per inviare agli utenti abilitati le notifiche ogni lunedi' alle 20:20 (facoltativo)
    #job = schedule.every().monday.at("20:20").do(send_notifications, context=dispatcher) # Per informazioni sullo scheduling vai qui https://schedule.readthedocs.io/en/stable/index.html, rimuovi '#' all'inizio

    # Registra il comando /monster
    monster_handler = CommandHandler('monster', monster_command)
    dispatcher.add_handler(monster_handler)

    # Avvia il bot
    updater.start_polling()

    # Avvia il ciclo di scheduling
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
