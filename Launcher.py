print("-=LOG OF Launcher.py=-")
print("Spouštím Launcher.py...")
print("importuji...")
import requests
import platform
import os
import subprocess
import sys
import json
import time
from urllib.parse import urlparse
# Importujeme všechny potřebné funkce z funcions_own
from funcions_own import update1, save_config, load_config, get_application_root

print("import dokončen.")

# --- Nastavení aktuálního pracovního adresáře na kořen aplikace ---
puvodni_cwd = os.getcwd()
print(f"Původní aktuální pracovní adresář (CWD): {puvodni_cwd}")

aplikacni_koren = get_application_root()
print(f"Zjištěný kořenový adresář aplikace (kde je skript/exe): {aplikacni_koren}")

try:
    os.chdir(aplikacni_koren)
    print(f"Aktuální pracovní adresář (CWD) změněn na: {os.getcwd()}")
except Exception as e:
    print(f"Chyba při změně adresáře na {aplikacni_koren}: {e}")

print("\n--- Pokračování programu ---")
print(f"Program nyní pracuje v adresáři: {os.getcwd()}")


print("Definuji lokální proměnné...")
# Definice cesty ke konfiguračnímu souboru
print("Definuji lokální proměnné - CONFIG_FILE, CONFIG_DIR, config...")
# Nyní se cesty k configu odvozují od aktuálního pracovního adresáře (který je již kořenem aplikace)
CONFIG_DIR = os.path.join(os.getcwd(), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

print(f"DEBUG: CONFIG_FILE nastaveno na: {CONFIG_FILE}")
print(f"DEBUG: CONFIG_DIR nastaveno na: {CONFIG_DIR}")

config = load_config(CONFIG_FILE) # Načtení konfigurace pomocí importované funkce
print(f"DEBUG: config načteno: {config}")
print("Definice lokálních proměnných dokončena.")
print("Kontroluji složku config...")
# Vytvoření složky config, pokud neexistuje
if not os.path.exists(CONFIG_DIR):
    print(f"DEBUG: Složka '{CONFIG_DIR}' neexistuje, vytvářím ji...")
    os.makedirs(CONFIG_DIR)
    print("Složka 'config' byla vytvořena.")
else:
    print(f"DEBUG: Složka '{CONFIG_DIR}' již existuje.")
print("Kontrola složky config dokončena.")

# Zajištění výchozích hodnot, pokud neexistují (mělo by být ošetřeno v load_config, ale pro jistotu)
print("Zajišťuji výchozí hodnoty v config...")
if "game_version" not in config:
    print("DEBUG: 'game_version' není v konfiguraci, nastavuji výchozí hodnotu.")
    config["game_version"] = "0.0.0" # Výchozí verze, pokud není nastavena
    print("Výchozí verze hry nastavena na 0.0.0.")
else:
    print(f"DEBUG: 'game_version' již existuje v konfiguraci: {config['game_version']}.")
print("Zajištění výchozích hodnot v config dokončena.")
print("Kontroluji cestu ke hře...")
# Kontrola a nastavení cesty ke hře
if "path_game" not in config or not os.path.exists(os.path.join(os.getcwd(), config["path_game"])):
    print("DEBUG: 'path_game' není v konfiguraci nebo cesta neexistuje.")
    path_game = input("Zadejte složku, ve které bude hra (relativní k adresáři launcheru, např. 'Game'): ")
    config["path_game"] = path_game
    save_config(CONFIG_FILE, config) # Uložíme nově zadanou cestu pomocí importované funkce
    print(f"Nastavená cesta ke hře: {config['path_game']}")
else:
    print(f"Nastavená cesta ke hře: {config['path_game']}")
print("Kontrola cesty ke hře dokončena.")

print("Kontroluji složku pro hru...")
# Vytvoření složky pro hru, pokud neexistuje
full_game_path_from_config = os.path.join(os.getcwd(), config["path_game"])
if not os.path.exists(full_game_path_from_config):
    print(f"DEBUG: Složka pro hru '{full_game_path_from_config}' neexistuje, vytvářím ji...")
    os.makedirs(full_game_path_from_config)
    print(f"Adresář '{full_game_path_from_config}' byl vytvořen.")
else:
    print(f"Adresář '{full_game_path_from_config}' již existuje.")
print("Kontrola složky pro hru dokončena.")
print("Definuji URL pro stažení verze hry z GitHubu...")
url_github_game_version = "https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/game.version"
print(f"DEBUG: URL pro verzi hry z GitHubu: {url_github_game_version}")

# Stažení souboru s verzí hry z GitHubu
print("Stahuji verzi hry z GitHubu...")
try:
    print(f"DEBUG: Pokouším se stáhnout z {url_github_game_version}")
    response_github_version = requests.get(url_github_game_version)
    response_github_version.raise_for_status()
    print(f"DEBUG: Status kód odpovědi GitHub verze: {response_github_version.status_code}")

    github_game_ver = response_github_version.content.decode('utf-8').strip()
    print(f"Verze hry z GitHubu: {github_game_ver}")

except requests.exceptions.RequestException as e:
    print(f"Chyba při stahování verze hry z GitHubu: {e}")
    github_game_ver = config["game_version"]
    print(f"Používám lokální verzi hry: {github_game_ver}")
except Exception as e:
    print(f"DEBUG: Nastala neočekávaná chyba při stahování verze hry: {e}")
    github_game_ver = config["game_version"]
    print(f"Používám lokální verzi hry jako zálohu: {github_game_ver}")


# Porovnání verzí a spuštění odpovídajícího skriptu
print(f"DEBUG: Porovnávám GitHub verzi ({github_game_ver}) s lokální verzí ({config['game_version']}).")
if github_game_ver == config["game_version"]:
    print("Verze hry je aktuální.")
    if platform.system() == "Windows":
        start_game_command = ["cmd.exe", "/C", "run.bat"]
        print(f"DEBUG: Systém je Windows, start_game_command nastaven na: {start_game_command}")
    else: # Předpokládáme Linux nebo macOS
        start_game_command = "./run.sh"
        print(f"DEBUG: Systém není Windows, start_game_command nastaven na: {start_game_command}")

    print(f"Spouštím hru: {start_game_command} v adresáři: {full_game_path_from_config}")
    try:
        print(f"DEBUG: Pokouším se spustit subprocess: {start_game_command} s cwd={full_game_path_from_config}")
        subprocess.run(start_game_command, check=True, cwd=full_game_path_from_config)
        print(f"DEBUG: Příkaz '{start_game_command}' byl úspěšně spuštěn.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spouštění příkazu '{start_game_command}': {e}")
        print(f"DEBUG: Návratový kód chyby: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}")
    except FileNotFoundError:
        print(f"Soubor '{start_game_command}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.")
        print(f"DEBUG: Cesta k souboru, který nebyl nalezen: {start_game_command}")
    except Exception as e:
        print(f"Nastala neočekávaná chyba při spouštění příkazu: {e}")
        print(f"DEBUG: Typ chyby: {type(e).__name__}")

else:
    print("Verze hry není aktuální. Stahuji aktualizaci.")
    print(f"DEBUG: Aktualizuji config['game_version'] z {config['game_version']} na {github_game_ver}.")
    config["game_version"] = github_game_ver
    save_config(CONFIG_FILE, config)
    print("DEBUG: Nová verze uložena do config.json.")

    # URL pro stažení aktualizace hry
    url_seznam_souboru = f"https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/{github_game_ver}/list.txt"
    print(f"DEBUG: URL pro seznam souborů aktualizace: {url_seznam_souboru}")

    # Složka, kam se stáhne samotný soubor list.txt (aktuální složka)
    slozka_pro_stahovani_seznamu = os.path.join(os.getcwd(), "download")
    print(f"DEBUG: Složka pro stahování seznamu: {slozka_pro_stahovani_seznamu}")

    # Název, pod kterým se lokálně uloží stažený seznam URL
    nazev_lokalniho_seznamu = "list.txt"
    print(f"DEBUG: Název lokálního seznamu: {nazev_lokalniho_seznamu}")

    # Cílová složka pro soubory, které jsou uvedeny v list.txt
    slozka_pro_stahovani_obsahu_seznamu = os.path.join(os.getcwd(), "download")
    print(f"DEBUG: Složka pro stahování obsahu seznamu: {slozka_pro_stahovani_obsahu_seznamu}")

    print(f"Stahuji soubor se seznamem URL z: {url_seznam_souboru}")

    try:
        print(f"DEBUG: Pokouším se stáhnout list.txt z {url_seznam_souboru}")
        response_list = requests.get(url_seznam_souboru)
        response_list.raise_for_status()
        print(f"DEBUG: Status kód odpovědi list.txt: {response_list.status_code}")

        cesta_k_lokalnimu_seznamu = os.path.join(slozka_pro_stahovani_seznamu, nazev_lokalniho_seznamu)
        print(f"DEBUG: Ukládám list.txt do: {cesta_k_lokalnimu_seznamu}")
        if not os.path.exists(slozka_pro_stahovani_seznamu):
            os.makedirs(slozka_pro_stahovani_seznamu)
            print(f"DEBUG: Složka '{slozka_pro_stahovani_seznamu}' byla vytvořena pro uložení list.txt.")

        with open(cesta_k_lokalnimu_seznamu, 'wb') as f:
            f.write(response_list.content)
        print(f"Seznam URL úspěšně stažen do: {cesta_k_lokalnimu_seznamu}")

        print(f"DEBUG: Volám funkci update1 s '{cesta_k_lokalnimu_seznamu}' a '{slozka_pro_stahovani_obsahu_seznamu}'.")
        update1(cesta_k_lokalnimu_seznamu, slozka_pro_stahovani_obsahu_seznamu)
        print("DEBUG: Funkce update1 dokončena.")

        print(f"DEBUG: Pokouším se smazat soubor: {cesta_k_lokalnimu_seznamu}")
        try:
            os.remove(cesta_k_lokalnimu_seznamu)
            print(f"Soubor '{nazev_lokalniho_seznamu}' byl úspěšně smazán.")
        except OSError as e:
            print(f"Chyba při mazání souboru '{nazev_lokalniho_seznamu}': {e}")
            print(f"DEBUG: Chyba OS při mazání: {e.strerror}")

    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování seznamu URL z GitHubu: {e}")
        print(f"DEBUG: Detaily chyby RequestException: {e}")
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {e}")
        print(f"DEBUG: Typ neočekávané chyby: {type(e).__name__}")

    if platform.system() == "Windows":
        start_command = ["cmd.exe", "/C", ".\\update.cmd", os.path.normpath(config['path_game'])]
        print(f"DEBUG: Systém je Windows, start_command pro aktualizaci nastaven na: {start_command}")
    else: # Předpokládáme Linux nebo macOS
        start_command = ["./update.sh", os.path.normpath(config['path_game'])]
        print(f"DEBUG: Systém není Windows, start_command pro aktualizaci nastaven na: {start_command}")

    print(f"Spouštím příkaz: {start_command}")
    try:
        print(f"DEBUG: Pokouším se spustit subprocess pro aktualizaci: {start_command}")
        subprocess.run(start_command, check=True)
        print(f"DEBUG: Příkaz '{start_command}' pro aktualizaci byl úspěšně spuštěn.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spouštění příkazu '{start_command}': {e}")
        print(f"DEBUG: Návratový kód chyby aktualizace: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}")
    except FileNotFoundError:
        print(f"Soubor '{start_command}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.")
        print(f"DEBUG: Cesta k souboru aktualizace, který nebyl nalezen: {start_command}")
    except Exception as e:
        print(f"Nastala neočekávaná chyba při spouštění příkazu: {e}")
        print(f"DEBUG: Typ chyby při spouštění aktualizace: {type(e).__name__}")

    # Po dokončení aktualizace externím skriptem se spustí hra
    if platform.system() == "Windows":
        start_game_command = ["cmd.exe", "/C", "run.bat"]
        print(f"DEBUG: Systém je Windows, start_game_command po aktualizaci nastaven na: {start_game_command}")
    else: # Předpokládáme Linux nebo macOS
        start_game_command = "./run.sh"
        print(f"DEBUG: Systém není Windows, start_game_command po aktualizaci nastaven na: {start_game_command}")

    print(f"Spouštím hru: {start_game_command} v adresáři: {full_game_path_from_config}")
    try:
        print(f"DEBUG: Pokouším se spustit subprocess pro hru po aktualizaci: {start_game_command}")
        subprocess.run(start_game_command, check=True, cwd=full_game_path_from_config)
        print(f"DEBUG: Příkaz '{start_game_command}' po aktualizaci byl úspěšně spuštěn.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spouštění hry '{start_game_command}' po aktualizaci: {e}")
        print(f"DEBUG: Návratový kód chyby hry po aktualizaci: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}")
    except FileNotFoundError:
        print(f"Soubor '{start_game_command}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.")
        print(f"DEBUG: Cesta k souboru hry po aktualizaci, který nebyl nalezen: {start_game_command}")
    except Exception as e:
        print(f"Nastala neočekávaná chyba při spouštění hry po aktualizaci: {e}")
        print(f"DEBUG: Typ chyby hry po aktualizaci: {type(e).__name__}")
