import os
import requests
from urllib.parse import urlparse
import json
import sys

def get_application_root():
    """
    Vrátí absolutní cestu ke kořenovému adresáři aplikace.
    Funguje pro normální spuštění Python skriptu i pro PyInstaller balíčky (--onedir, --onefile).
    """
    if getattr(sys, 'frozen', False):
        # Jsme spuštěni jako PyInstaller balíček (např. .exe)
        # sys.executable je cesta k samotnému spustitelnému souboru (.exe)
        # os.path.dirname() získá adresář, ve kterém je tento .exe soubor
        return os.path.dirname(sys.executable)
    else:
        # Jsme spuštěni jako normální Python skript (během vývoje)
        # __file__ je cesta k tomuto skriptu
        # os.path.abspath(__file__) zajistí, že je to absolutní cesta
        # os.path.dirname() získá adresář, ve kterém je tento skript
        return os.path.dirname(os.path.abspath(__file__))

def save_config(config_file_path, config_data):
    """
    Uloží konfigurační data do souboru JSON.
    """
    try:
        # Zajistí, že adresář pro config soubor existuje
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        # Ukládáme všechna data, která jsou v config_data
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        print(f"Konfigurace úspěšně uložena do '{config_file_path}'.")
    except Exception as e:
        print(f"Chyba při ukládání konfigurace: {e}")

def load_config(config_file_path):
    """
    Načte konfigurační data ze souboru JSON.
    Pokud soubor neexistuje nebo je chybný, vytvoří/použije výchozí konfiguraci.
    """
    default_config = {
        "path_game": "Game/",
        "game_version": "0.0.0",
        "platform_version": "Win64"
    }
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        # Zajistí, že výchozí hodnoty jsou přítomny, pokud nejsou v souboru
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
        return config
    except FileNotFoundError:
        print(f"Chyba: Soubor '{config_file_path}' nebyl nalezen. Vytvářím výchozí konfiguraci.")
        save_config(config_file_path, default_config) # Použijeme nově definovanou save_config
        return default_config
    except json.JSONDecodeError:
        print(f"Chyba: Chybný formát JSON v souboru '{config_file_path}'. Používám výchozí konfiguraci.")
        save_config(config_file_path, default_config) # Použijeme nově definovanou save_config
        return default_config
    except Exception as e:
        print(f"Nastala neočekávaná chyba při načítání souboru '{config_file_path}': {e}")
        save_config(config_file_path, default_config)
        return default_config

def update1(soubor_s_url: str, cilova_slozka: str):
    """
    Stáhne soubory z URL adres uvedených v textovém souboru
    a uloží je do zadané složky se zachováním původních názvů.

    Args:
        soubor_s_url (str): Cesta k textovému souboru, kde je na každém řádku 1 URL.
        cilova_slozka (str): Cesta k cílové složce, kam se soubory uloží.
    """
    if not os.path.exists(cilova_slozka):
        os.makedirs(cilova_slozka)
        print(f"Vytvořena složka: {cilova_slozka}")

    try:
        with open(soubor_s_url, 'r', encoding='utf-8') as f:
            urls = f.readlines()
    except FileNotFoundError:
        print(f"Chyba: Soubor '{soubor_s_url}' s URL adresami nebyl nalezen.")
        return

    stazeno_uspesne = 0
    stazeno_selhalo = 0

    print(f"Začínám stahování souborů do složky '{cilova_slozka}' z lokálního seznamu.")

    for radek_url in urls:
        url = radek_url.strip()
        if not url:
            continue

        try:
            parsed_url = urlparse(url)
            nazev_souboru = os.path.basename(parsed_url.path)

            if not nazev_souboru:
                print(f"Upozornění: Nelze získat název souboru z URL: {url}. Přeskakuji toto URL.")
                continue

            cesta_k_souboru = os.path.join(cilova_slozka, nazev_souboru)

            print(f"Stahuji '{url}' do '{cesta_k_souboru}'...")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(cesta_k_souboru, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Úspěšně staženo: {nazev_souboru}")
            stazeno_uspesne += 1

        except requests.exceptions.RequestException as e:
            print(f"Chyba při stahování {url}: {e}")
            stazeno_selhalo += 1
        except Exception as e:
            print(f"Nastala neočekávaná chyba u {url}: {e}")
            stazeno_selhalo += 1

    print("\n--- Stahování obsahu seznamu dokončeno ---")
    print(f"Celkem staženo úspěšně: {stazeno_uspesne}")
    print(f"Celkem selhalo: {stazeno_selhalo}")
