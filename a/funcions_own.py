import os
import requests
from urllib.parse import urlparse
import json
def update1(soubor_s_url: str, cilova_slozka: str):
    """
    Stáhne soubory z URL adres uvedených v textovém souboru
    a uloží je do zadané složky se zachováním původních názvů.

    Args:
        soubor_s_url (str): Cesta k textovému souboru, kde je na každém řádku 1 URL.
        cilova_slozka (str): Cesta k cílové složce, kam se soubory uloží.
    """
    # Vytvoříme cílovou složku, pokud neexistuje
    # os.makedirs s exist_ok=True zabrání chybě, pokud složka již existuje
    if not os.path.exists(cilova_slozka):
        os.makedirs(cilova_slozka)
        print(f"Vytvořena složka: {cilova_slozka}")

    try:
        # Otevřeme soubor s URL adresami pro čtení
        # Používáme 'utf-8' kódování pro širokou kompatibilitu
        with open(soubor_s_url, 'r', encoding='utf-8') as f:
            urls = f.readlines() # Přečteme všechny řádky do seznamu
    except FileNotFoundError:
        print(f"Chyba: Soubor '{soubor_s_url}' s URL adresami nebyl nalezen.")
        return # Ukončíme funkci, pokud soubor neexistuje

    stazeno_uspesne = 0 # Počítadlo úspěšně stažených souborů
    stazeno_selhalo = 0 # Počítadlo souborů, u kterých došlo k chybě

    print(f"Začínám stahování souborů do složky '{cilova_slozka}' z lokálního seznamu.")

    # Projdeme každou URL adresu v seznamu
    for radek_url in urls:
        url = radek_url.strip() # Odstraníme bílé znaky (mezery, nové řádky) z URL

        if not url: # Přeskočíme prázdné řádky v souboru
            continue

        try:
            # Získání názvu souboru z URL
            # urlparse rozdělí URL na komponenty (schéma, síťová adresa, cesta atd.)
            # os.path.basename získá název souboru z cesty (poslední část po lomítku)
            parsed_url = urlparse(url)
            nazev_souboru = os.path.basename(parsed_url.path)

            if not nazev_souboru:
                print(f"Upozornění: Nelze získat název souboru z URL: {url}. Přeskakuji toto URL.")
                continue

            # Sestavíme kompletní cestu k souboru, kam se má uložit
            cesta_k_souboru = os.path.join(cilova_slozka, nazev_souboru)

            print(f"Stahuji '{url}' do '{cesta_k_souboru}'...")
            
            # Provedeme HTTP GET požadavek na URL
            # stream=True je důležité pro velké soubory, aby se stahovaly po částech a nezatížily paměť
            response = requests.get(url, stream=True)
            
            # Zkontrolujeme, zda byl požadavek úspěšný (status kód 200)
            # raise_for_status() vyvolá HTTPError pro chybové status kódy (4xx, 5xx)
            response.raise_for_status() 

            # Otevřeme soubor pro zápis v binárním režimu ('wb')
            with open(cesta_k_souboru, 'wb') as f:
                # Iterujeme přes obsah odpovědi po částech (chunks)
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk) # Zapisujeme jednotlivé části do souboru
            
            print(f"Úspěšně staženo: {nazev_souboru}")
            stazeno_uspesne += 1 # Zvýšíme počítadlo úspěšných stažení

        except requests.exceptions.RequestException as e:
            # Zachytíme chyby související s požadavky (síť, HTTP chyby atd.)
            print(f"Chyba při stahování {url}: {e}")
            stazeno_selhalo += 1 # Zvýšíme počítadlo neúspěšných stažení
        except Exception as e:
            # Zachytíme jakékoli jiné neočekávané chyby
            print(f"Nastala neočekávaná chyba u {url}: {e}")
            stazeno_selhalo += 1 # Zvýšíme počítadlo neúspěšných stažení

    print("\n--- Stahování obsahu seznamu dokončeno ---")
    print(f"Celkem staženo úspěšně: {stazeno_uspesne}")
    print(f"Celkem selhalo: {stazeno_selhalo}")
def load_config():
    """
    Načte konfiguraci ze souboru config.json.
    Pokud soubor existuje, přečte jeho obsah a vrátí ho jako Python slovník.
    Pokud soubor neexistuje, vrátí prázdný slovník.
    """
    CONFIG_FILE = "./config/config.json" # Definice cesty ke konfiguračnímu souboru
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {} # Vrátí prázdný slovník, pokud soubor neexistuje

# Funkce pro ukládání konfigurace
def save_config(config):
    """
    Uloží zadaný konfigurační slovník do souboru config.json.
    Ukládá ho s odsazením 4 mezer pro lepší čitelnost.
    """
    CONFIG_FILE = "./config/config.json" # Definice cesty ke konfiguračnímu souboru
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4) # Ukládá s odsazením pro lepší čitelnost

def update_game_version_to_0_0_0(config_file_path="./config/config.json"):
    """
    Updates the 'game_version' in the config.json file to "0.0.0".
    If the config directory or file does not exist, it creates them.
    """
    print(f"DEBUG: Pokouším se aktualizovat 'game_version' v souboru: {config_file_path}")

    config_dir = os.path.dirname(config_file_path)
    
    # 1. Zkontrolujte a vytvořte složku config, pokud neexistuje
    if not os.path.exists(config_dir):
        print(f"DEBUG: Složka '{config_dir}' neexistuje, vytvářím ji...")
        os.makedirs(config_dir)
        print(f"Složka '{config_dir}' byla vytvořena.")
    else:
        print(f"DEBUG: Složka '{config_dir}' již existuje.")

    config_data = {}
    
    # 2. Zkontrolujte, zda soubor config.json existuje a načtěte ho, nebo vytvořte výchozí
    if os.path.exists(config_file_path):
        print(f"DEBUG: Soubor '{config_file_path}' existuje, načítám obsah.")
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            print(f"DEBUG: Konfigurace načtena: {config_data}")
        except json.JSONDecodeError as e:
            print(f"Chyba: Nepodařilo se načíst JSON ze souboru '{config_file_path}': {e}")
            print("Vytvářím výchozí konfiguraci.")
            config_data = {"game_version": "0.0.0", "path_game": ""}
        except Exception as e:
            print(f"Nastala neočekávaná chyba při čtení souboru '{config_file_path}': {e}")
            print("Vytvářím výchozí konfiguraci.")
            config_data = {"game_version": "0.0.0", "path_game": ""}
    else:
        print(f"Konfiguracni soubor '{config_file_path}' nebyl nalezen, vytvarim vychozi...")
        config_data = {"game_version": "0.0.0", "path_game": ""}
        print(f"DEBUG: Vytvořena výchozí konfigurace: {config_data}")

    # 3. Přepište hodnotu game_version
    old_version = config_data.get("game_version", "Neznámá")
    config_data["game_version"] = "0.0.0"
    print(f"Přepisuji 'game_version' z '{old_version}' na '0.0.0'.")

    # 4. Uložte aktualizovanou konfiguraci zpět do souboru
    try:
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4) # Použijte indent pro pěkné formátování
        print(f"Radek 'game_version' byl uspesne prepsan v souboru '{config_file_path}'.")
    except Exception as e:
        print(f"Chyba při zápisu do souboru '{config_file_path}': {e}")


