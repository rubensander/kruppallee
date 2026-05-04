import requests
import json
import logging
import pandas as pd

pd.set_option('display.max_columns', None)


# Beispiel-URL (öffentliche API)
url = "https://ifa.ruhrbahn.de/departure/20009289" #9409

# GET-Anfrage senden
response = requests.get(url)

# Statuscode prüfen
if response.status_code == 200:
    data = response.json()  # Antwort als JSON lesen
    departure_list = data["data"]["departureList"]
    #print([key for key, value in departure_list[0]["servingLine"].items()])
    dict_lines = []
    for departure in departure_list[:30]:
        if "realDateTime" in departure:
            dict_lines.append(departure["servingLine"])
            line = departure["servingLine"]
            time = departure["realDateTime"]["hour"] + ":" + departure["realDateTime"]["minute"]
            print(f"Linie: {line['number']}, Richtung: {line['direction']}, Abfahrtszeit: {time}, Verspätung: {line['delay']} Minuten")
            #print([value for key, value in line.items()])
    
    df_lines = pd.DataFrame(dict_lines)
    print(df_lines.sort_values(by="key"))
else:
    print("Fehler:", response.status_code)