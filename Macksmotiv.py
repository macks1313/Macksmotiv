import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import openai
import os

# Configuration de l'API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Récupération des chemins pour Chromium et Chromedriver
CHROME_BIN = os.getenv("GOOGLE_CHROME_BIN", "/usr/bin/chromium-browser")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

# Débogage pour vérifier les chemins
def debug_paths():
    print("Chemin défini de Chromium :", CHROME_BIN)
    print("Chemin défini de Chromedriver :", CHROMEDRIVER_PATH)

    result_chrome = subprocess.run(['which', 'chromium-browser'], stdout=subprocess.PIPE)
    result_driver = subprocess.run(['which', 'chromedriver'], stdout=subprocess.PIPE)

    print("Résultat 'which chromium-browser':", result_chrome.stdout.decode().strip())
    print("Résultat 'which chromedriver':", result_driver.stdout.decode().strip())

debug_paths()

# Configuration des options de Selenium
chrome_options = Options()
chrome_options.binary_location = CHROME_BIN  # Utilisation du chemin défini pour Chromium
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")

# Initialisation du driver avec le chemin explicite de Chromedriver
try:
    driver = webdriver.Chrome(
        service=Service(CHROMEDRIVER_PATH),
        options=chrome_options
    )
except Exception as e:
    print("Erreur lors de l'initialisation de Selenium :", str(e))
    raise

# Identifiants Twitter
USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")

# Fonction pour se connecter à Twitter
def login_twitter():
    driver.get("https://twitter.com/login")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, "text")
    username_input.send_keys(USERNAME)
    username_input.send_keys(Keys.RETURN)
    time.sleep(3)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)

# Générer un tweet sarcastique et motivant
def generate_tweet():
    prompt = (
        "Crée un tweet sarcastique mais motivant, de moins de 270 caractères, "
        "avec des hashtags populaires adaptés à une page de développement personnel."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un expert en développement personnel sarcastique."},
            {"role": "user", "content": prompt}
        ]
    )

    tweet = response.choices[0].message['content'].strip()
    return tweet

# Fonction pour poster un tweet
def post_tweet(tweet):
    driver.get("https://twitter.com/compose/tweet")
    time.sleep(5)

    tweet_input = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
    tweet_input.send_keys(tweet)

    tweet_button = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
    tweet_button.click()

    time.sleep(5)

# Répondre aux mentions
def respond_to_mentions():
    driver.get("https://twitter.com/notifications/mentions")
    time.sleep(5)

    mentions = driver.find_elements(By.XPATH, "//div[@data-testid='tweet']")
    for mention in mentions[:3]:
        try:
            mention.click()
            time.sleep(3)

            response = generate_tweet()
            reply_input = driver.find_element(By.XPATH, "//div[@aria-label='Tweet text']")
            reply_input.send_keys(response)

            reply_button = driver.find_element(By.XPATH, "//div[@data-testid='tweetButton']")
            reply_button.click()
            time.sleep(3)
        except Exception as e:
            print("Erreur lors de la réponse à une mention :", e)

# Répondre automatiquement aux DM
def respond_to_dms():
    driver.get("https://twitter.com/messages")
    time.sleep(5)

    dms = driver.find_elements(By.XPATH, "//div[@data-testid='conversation']")
    for dm in dms[:3]:
        try:
            dm.click()
            time.sleep(3)

            messages = driver.find_elements(By.XPATH, "//div[@data-testid='messageEntry']")
            if messages:
                last_message = messages[-1].text
                response = generate_tweet()

                message_input = driver.find_element(By.XPATH, "//div[@aria-label='Message']")
                message_input.send_keys(response)
                message_input.send_keys(Keys.RETURN)
                time.sleep(3)
        except Exception as e:
            print("Erreur lors de la réponse à un DM :", e)

# Fonction principale pour lancer le bot
def run_bot():
    login_twitter()

    tweet_count = 0
    while True:
        try:
            tweet = generate_tweet()
            post_tweet(tweet)

            tweet_count += 1
            if tweet_count % 5 == 0:
                # Créer un thread tous les 5 tweets
                thread_tweet = (
                    "Voici un thread de motivation sarcastique. 🧵\n\n"
                    "1/ Ce n'est pas parce que tu as échoué aujourd'hui que tu ne vas pas échouer demain. "
                    "Mais bon, il faut bien commencer quelque part.\n"
                    "2/ L'échec est un apprentissage. Si tu veux vraiment réussir, accumule les échecs plus vite.\n"
                    "3/ Dernier conseil : dors... ou pas."
                )
                post_tweet(thread_tweet)

            # Répondre aux mentions et DM
            respond_to_mentions()
            respond_to_dms()

            # Attendre 110 minutes avant le prochain tweet
            time.sleep(110 * 60)

        except Exception as e:
            print("Erreur dans l'exécution du bot :", e)
            time.sleep(60)

# Lancer le bot
if __name__ == "__main__":
    run_bot()