import requests, json, tweepy, os, random, csv, sys
from dotenv import load_dotenv

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

def get_csv(response):
  # https://stackoverflow.com/questions/35371043/use-python-requests-to-download-csv
  return response.content.decode('ISO-8859-1')

def compare_csv(oldfile,response):
  # https://stackoverflow.com/a/44299915
  filesize = int(os.stat(oldfile).st_size)
  responsesize = int(response.headers['Content-length'])

  if responsesize == filesize:
    return True
  else:
    return False

def store_csv(content,location):
  csvfile = open(location, 'wb') 
  csvfile.write(content) 
  csvfile.close()

def get_latest(covidcsv,zona):
  for row in covidcsv:
    if row['zona_basica_salud'] == zona:
      return row

def save_to_json(data,file):
  with open(file, 'w') as fp:
    json.dump(data, fp)

def compare_json(data,file):
  # Open the previous json data
  try:
    with open(file) as json_file:
      previous = json.load(json_file)
  except:
    previous = {}

  # If the results are the same, do nothing
  if previous == data:
    return False
  else:
    # Otherwise, save the file for next execution and continue
    save_to_json(data,file)
    return True

def generate_tweet(data):
  tweet='''\
  {zona} ({fecha})
  Últimos 14 días:
  • Confirmados: {confirmados_14_dias}
  • Incidencia acumulada: {incidencia_14_dias}
  Totales:
  • Confirmados: {confirmados_totales}
  • Incidencia acumulada: {incidencia_totales}
  #LasRozas
  '''.format(zona=data["zona_basica_salud"], \
             fecha=data["fecha_informe"], \
             confirmados_14_dias = data["casos_confirmados_ultimos_14dias"], \
             incidencia_14_dias = data["tasa_incidencia_acumulada_ultimos_14dias"], \
             confirmados_totales = data["casos_confirmados_totales"], \
             incidencia_totales = data["tasa_incidencia_acumulada_total"])
  return tweet

def publish_tweet(data):
  # Authenticate to Twitter
  auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

  # Create API object
  api = tweepy.API(auth)
  api.update_status(data)

def main():  
  try:
    response = requests.get(COVID_URL, stream=True)
    response.raise_for_status()
  except requests.exceptions.HTTPError as err:
    raise SystemExit(err)
  # https://stackoverflow.com/a/44299915
  if compare_csv(CSVFILE,response):
    sys.exit("Dupe")
  else:
    store_csv(response.content,CSVFILE)
  covidcsv = csv.DictReader(get_csv(response).splitlines(), delimiter=";", quoting=csv.QUOTE_NONE)
  
  latest={}
  for zona in zonas:
    latest[zona]=get_latest(covidcsv,zona)
    if compare_json(latest[zona],zona+".json"):
      tweet=generate_tweet(latest[zona])
      #publish_tweet(tweet)
      print(tweet)

if __name__ == "__main__":
    main()
