import subprocess
import os
import json
import platform

# Funkce pro načtení konfigurace (zkopírováno z funcions_own.py pro samostatnost)
def load_config():
    """
    Načte konfiguraci ze souboru config.json.
    Pokud soubor existuje, přečte jeho obsah a vrátí ho jako Python slovník.
    Pokud soubor neexistuje nebo je poškozený, vrátí výchozí konfiguraci
    a pokusí se ji uložit.
    """
    CONFIG_FILE = "./config/config.json" # Definice cesty ke konfiguračnímu souboru
    default_config = {
        "game_version": "0.0.0", # Výchozí verze
        "path_game": "Game/", # Výchozí cesta ke hře
        "platform_version": "Win64" # Výchozí platforma
    }

    config_data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            # Zajistíme, že v načtené konfiguraci jsou všechny výchozí klíče
            for key, default_value in default_config.items():
                if key not in config_data:
                    config_data[key] = default_value
        except json.JSONDecodeError as e:
            print(f"Chyba: Nepodařilo se načíst JSON ze souboru '{CONFIG_FILE}': {e}")
            print("Vytvářím/používám výchozí konfiguraci.")
            config_data = default_config.copy() # Použijeme kopii výchozí konfigurace
            save_config_simple(config_data) # Pokusíme se uložit výchozí konfiguraci
        except Exception as e:
            print(f"Nastala neočekávaná chyba při čtení souboru '{CONFIG_FILE}': {e}")
            print("Vytvářím/používám výchozí konfiguraci.")
            config_data = default_config.copy() # Použijeme kopii výchozí konfigurace
            save_config_simple(config_data) # Pokusíme se uložit výchozí konfiguraci
    else:
        print(f"Konfigurační soubor '{CONFIG_FILE}' nebyl nalezen, vytvářím výchozí...")
        config_data = default_config.copy() # Použijeme kopii výchozí konfigurace
        save_config_simple(config_data) # Uložíme výchozí konfiguraci

    return config_data

# Zjednodušená funkce save_config pro tento skript, ukládá všechny klíče
def save_config_simple(config):
    """
    Uloží zadaný konfigurační slovník do souboru config.json.
    """
    CONFIG_FILE = "./config/config.json"
    CONFIG_DIR = os.path.dirname(CONFIG_FILE)

    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        print(f"Vytvořena složka: {CONFIG_DIR}")

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

def run_updater():
    """
    Načte konfiguraci a spustí update.cmd/update.sh s parametry.
    """
    print("Spouštím run_updater.py...")
    
    # Načtení konfigurace
    config = load_config()
    
    # Získání parametrů z konfigurace
    path_game = config.get("path_game", "Game/")
    platform_version = config.get("platform_version", "Win64")

    # Zajištění, že path_game je absolutní cesta (pokud je relativní k tomuto skriptu)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_path_game = os.path.join(script_dir, path_game)
    
    # Normalizace cesty pro konzistentní formát
    normalized_path_game = os.path.normpath(absolute_path_game)

    print(f"Načtená path_game: {normalized_path_game}")
    print(f"Načtená platform_version: {platform_version}")

    command = []
    if platform.system() == "Windows":
        updater_script = "update.bat"
        # Používáme cmd.exe /C pro spuštění .cmd souboru
        # Parametry předáváme jako samostatné argumenty
        command = ["cmd.exe", "/C", updater_script, normalized_path_game, platform_version]
    else: # Předpokládáme Linux nebo macOS
        updater_script = "update.sh"
        # Příkaz je seznam argumentů
        command = ["bash", updater_script, normalized_path_game, platform_version] # Používáme bash pro spolehlivé spuštění .sh

    print(f"Spouštím příkaz: {command}")
    try:
        # Spustí příkaz. check=True zajistí, že se vyvolá CalledProcessError, pokud příkaz selže.
        # cwd je nastaven na adresář skriptu, aby se updater_script našel
        subprocess.run(command, check=True, cwd=script_dir)
        print(f"Příkaz '{' '.join(command)}' byl úspěšně spuštěn.")
    except FileNotFoundError:
        print(f"Chyba: Aktualizační skript '{updater_script}' nebyl nalezen v '{script_dir}'.")
        print("Ujistěte se, že soubor existuje a je spustitelný.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spouštění aktualizačního skriptu: {e}")
        print(f"Návratový kód: {e.returncode}")
        if e.stdout:
            print(f"Standardní výstup: {e.stdout.decode()}")
        if e.stderr:
            print(f"Standardní chyba: {e.stderr.decode()}")
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {e}")

if __name__ == "__main__":
    run_updater()
