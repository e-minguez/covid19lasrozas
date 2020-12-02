import requests, json, tweepy, os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

COVID_URL = os.getenv("COVID_URL_LASROZAS")
CSVFILE = os.getenv("COVID_CSV")
JSONFILE = os.getenv("JSON_FILE")

hashtag = "#LasRozas"
zonas = ["La Marazuela","Las Matas","Las Rozas","Monterrozas"]

def save_data(data,zona):
  myfile=zona+".json"
  with open(myfile, 'w') as fp:
    json.dump(data, fp)

def compare_data(data,zona):
  myfile=zona+".json"
  # Open the previous json data
  try:
    with open(myfile) as json_file:
      previous = json.load(json_file)
  except:
    previous = {}

  # If the results are the same, do nothing
  if previous == data:
    return True
  else:
    # Otherwise, save the file for next execution and continue
    save_data(data,zona)
    return False

def generate_tweet(data):
  dt = datetime.strptime(data["fecha_informe"], '%Y-%m-%dT%H:%M:%S')
  datecorrected="{}/{}/{}".format(dt.day,dt.month,dt.year)
  tweet='''\
  {zona} ({fecha})
  Últimos 14 días:
  • Confirmados: {confirmados_14_dias}
  • Incidencia acumulada: {incidencia_14_dias}
  Totales:
  • Confirmados: {confirmados_totales}
  • Incidencia acumulada: {incidencia_totales}
  {hashtag}
  '''.format(zona=data["zona_basica_salud"], \
             fecha=datecorrected, \
             confirmados_14_dias = data["casos_confirmados_ultimos_14dias"], \
             incidencia_14_dias = data["tasa_incidencia_acumulada_ultimos_14dias"], \
             confirmados_totales = data["casos_confirmados_totales"], \
             incidencia_totales = data["tasa_incidencia_acumulada_total"], \
             hashtag=hashtag)
  return tweet

def publish_tweet(data):
  # Authenticate to Twitter
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  # Create API object
  api = tweepy.API(auth)
  api.update_status(data)

def main():
  for zona in zonas:
    url=COVID_URL.format(zona=zona)
    try:
      response = requests.get(url)
      response.raise_for_status()
    except requests.exceptions.HTTPError as err:
      raise SystemExit(err)
    data=response.json()["result"]["records"][0]
    if compare_data(data,zona):
      print(zona+" dupe")
    else:
      tweet=generate_tweet(data)
      publish_tweet(tweet)
      print(tweet)

if __name__ == "__main__":
    main()
