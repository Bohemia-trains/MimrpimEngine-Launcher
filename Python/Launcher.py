import sys
import os
import requests
import platform
import subprocess
import json
import time
from urllib.parse import urlparse
# Importujeme všechny potřebné funkce a třídu Logger z funcions_own
from funcions_own import Logger, get_application_root, save_config, load_config, download_file_with_progress, update1

# --- Nastavení logování do souboru ---
# Přesměrujeme sys.stdout na naši instanci Loggeru
# Tím se veškerý výstup z print() a dalších funkcí přesměruje.
sys.stdout = Logger()
version = "1.0.1"  # Verze aplikace, kterou budeme zobrazovat v titulku okna
os.system(f'title"Train simulator Czechia Launcher - Version {version}"')

# Konstanty pro barvy
RESET = "\033[0m"
RED = "\033[31m"      # Pro chyby
GREEN = "\033[32m"    # Pro úspěšné operace, dokončení
YELLOW = "\033[33m"   # Pro varování, uživatelský vstup, důležité informace
BLUE = "\033[34m"     # Pro obecné informace, úvodní zprávy
CYAN = "\033[36m"     # Pro debugovací zprávy
GREY = "\033[90m"     # Pro méně důležité, "tiché" zprávy

print(f"{BLUE}-=LOG OF Launcher.py=-{RESET}")
print(f"{BLUE}Spouštím Launcher.py...{RESET}")
print(f"{BLUE}Importuji...{RESET}")

print(f"{BLUE}Import dokončen.{RESET}")

# --- Nastavení aktuálního pracovního adresáře na kořen aplikace ---
puvodni_cwd = os.getcwd()
print(f"{BLUE}Původní aktuální pracovní adresář (CWD): {puvodni_cwd}{RESET}")

aplikacni_koren = get_application_root()
print(f"{BLUE}Zjištěný kořenový adresář aplikace (kde je skript/exe): {aplikacni_koren}{RESET}")

try:
    os.chdir(aplikacni_koren)
    print(f"{GREEN}Aktuální pracovní adresář (CWD) změněn na: {os.getcwd()}{RESET}")
except Exception as e:
    print(f"{RED}Chyba při změně adresáře na {aplikacni_koren}: {e}{RESET}")

print(f"\n{BLUE}--- Pokračování programu ---{RESET}")
print(f"{BLUE}Program nyní pracuje v adresáři: {os.getcwd()}{RESET}")


print(f"{BLUE}Definuji lokální proměnné...{RESET}")
# Definice cesty ke konfiguračnímu souboru
print(f"{BLUE}Definuji lokální proměnné - CONFIG_FILE, CONFIG_DIR, config...{RESET}")
# Nyní se cesty k configu odvozují od aktuálního pracovního adresáře (který je již kořenem aplikace)
CONFIG_DIR = os.path.join(os.getcwd(), "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

print(f"{CYAN}DEBUG: CONFIG_FILE nastaveno na: {CONFIG_FILE}{RESET}")
print(f"{CYAN}DEBUG: CONFIG_DIR nastaveno na: {CONFIG_DIR}{RESET}")

config = load_config(CONFIG_FILE) # Načtení konfigurace pomocí importované funkce
print(f"{CYAN}DEBUG: config načteno: {config}{RESET}")
print(f"{BLUE}Definice lokálních proměnných dokončena.{RESET}")
print(f"{BLUE}Kontroluji složku config...{RESET}")
# Vytvoření složky config, pokud neexistuje
if not os.path.exists(CONFIG_DIR):
    print(f"{CYAN}DEBUG: Složka '{CONFIG_DIR}' neexistuje, vytvářím ji...{RESET}")
    os.makedirs(CONFIG_DIR)
    print(f"{GREEN}Složka 'config' byla vytvořena.{RESET}")
else:
    print(f"{CYAN}DEBUG: Složka '{CONFIG_DIR}' již existuje.{RESET}")
print(f"{BLUE}Kontrola složky config dokončena.{RESET}")

# Zajištění výchozích hodnot, pokud neexistují (mělo by být ošetřeno v load_config, ale pro jistotu)
print(f"{BLUE}Zajišťuji výchozí hodnoty v config...{RESET}")
if "game_version" not in config:
    print(f"{CYAN}DEBUG: 'game_version' není v konfiguraci, nastavuji výchozí hodnotu.{RESET}")
    config["game_version"] = "0.0.0" # Výchozí verze, pokud není nastavena
    print(f"{YELLOW}Výchozí verze hry nastavena na 0.0.0.{RESET}")
else:
    print(f"{CYAN}DEBUG: 'game_version' již existuje v konfiguraci: {config['game_version']}.{RESET}")
print(f"{BLUE}Zajištění výchozích hodnot v config dokončena.{RESET}")

print(f"{BLUE}Kontroluji a vytvářím složku pro hru...{RESET}")
# Vytvoření složky pro hru, pokud neexistuje, před kontrolou a případným dotazem
# Normalizace cesty pro konzistentní formát
full_game_path_from_config = '"'+os.path.normpath(os.path.join(os.getcwd(), config.get("path_game", "Game/")))+'"'
if not os.path.exists(full_game_path_from_config):
    print(f"{CYAN}DEBUG: Složka pro hru '{full_game_path_from_config}' neexistuje, vytvářím ji...{RESET}")
    os.makedirs(full_game_path_from_config)
    print(f"{GREEN}Adresář '{full_game_path_from_config}' byl vytvořen.{RESET}")
else:
    print(f"{GREEN}Adresář '{full_game_path_from_config}' již existuje.{RESET}")
print(f"{BLUE}Kontrola a vytvoření složky pro hru dokončena.{RESET}")


print(f"{BLUE}Kontroluji cestu ke hře v konfiguraci...{RESET}")
# Kontrola a nastavení cesty ke hře
# Nyní se ptáme jen v případě, že 'path_game' není v konfiguraci vůbec
if "path_game" not in config:
    print(f"{CYAN}DEBUG: 'path_game' není v konfiguraci.{RESET}")
    path_game = input(f"{YELLOW}Zadejte složku, ve které bude hra (relativní k adresáři launcheru, např. 'Game'): {RESET}")
    config["path_game"] = path_game
    save_config(CONFIG_FILE, config) # Uložíme nově zadanou cestu pomocí importované funkce
    print(f"{YELLOW}Nastavená cesta ke hře: {config['path_game']}{RESET}")
else:
    print(f"{YELLOW}Nastavená cesta ke hře: {config['path_game']}{RESET}")
print(f"{BLUE}Kontrola cesty ke hře v konfiguraci dokončena.{RESET}")


print(f"{BLUE}Definuji URL pro stažení verze hry z GitHubu...{RESET}")
url_github_game_version = "https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/game.version"
print(f"{CYAN}DEBUG: URL pro verzi hry z GitHubu: {url_github_game_version}{RESET}")

# Stažení souboru s verzí hry z GitHubu
print(f"{BLUE}Stahuji verzi hry z GitHubu...{RESET}")
# Použijeme download_file_with_progress pro stažení game.version
temp_game_version_file = os.path.join(os.getcwd(), "game.version.tmp")
try:
    print(f"{CYAN}DEBUG: Pokouším se stáhnout game.version z {url_github_game_version}{RESET}")
    # Před stažením souboru game.version.tmp zajistíme, že existuje adresář
    # V tomto případě se stahuje do kořenového adresáře, takže není potřeba vytvářet podsložku
    download_file_with_progress(url_github_game_version, temp_game_version_file)

    with open(temp_game_version_file, 'r', encoding='utf-8') as f:
        github_game_ver = f.read().strip()
    print(f"{GREEN}Verze hry z GitHubu: {github_game_ver}{RESET}")

    # Po přečtení dočasný soubor smažeme
    os.remove(temp_game_version_file)
    print(f"{CYAN}DEBUG: Dočasný soubor '{temp_game_version_file}' smazán.{RESET}")

except requests.exceptions.RequestException as e:
    print(f"{RED}Chyba při stahování verze hry z GitHubu: {e}{RESET}")
    github_game_ver = config["game_version"]
    print(f"{YELLOW}Používám lokální verzi hry: {github_game_ver}{RESET}")
except FileNotFoundError:
    print(f"{RED}Chyba: Dočasný soubor '{temp_game_version_file}' nebyl nalezen po stažení. Používám lokální verzi.{RESET}")
    github_game_ver = config["game_version"]
except Exception as e:
    print(f"{RED}Nastala neočekávaná chyba při stahování verze hry: {e}{RESET}")
    print(f"{CYAN}DEBUG: Detaily chyby: {e}{RESET}")
    github_game_ver = config["game_version"]
    print(f"{YELLOW}Používám lokální verzi hry jako zálohu: {github_game_ver}{RESET}")


# Porovnání verzí a spuštění odpovídajícího skriptu
print(f"{BLUE}Porovnávám GitHub verzi ({github_game_ver}) s lokální verzí ({config['game_version']}).{RESET}")
if github_game_ver == config["game_version"]:
    print(f"{GREEN}Verze hry je aktuální.{RESET}")
    if platform.system() == "Windows":
        start_game_command = ["cmd.exe", "/C", "run.bat"]
        print(f"{CYAN}DEBUG: Systém je Windows, start_game_command nastaven na: {start_game_command}{RESET}")
    else: # Předpokládáme Linux nebo macOS
        start_game_command = "./run.sh"
        print(f"{CYAN}DEBUG: Systém není Windows, start_game_command nastaven na: {start_game_command}{RESET}")

    print(f"{YELLOW}Spouštím hru: {start_game_command} v adresáři: {full_game_path_from_config}{RESET}")
    try:
        print(f"{CYAN}DEBUG: Pokouším se spustit subprocess: {start_game_command} s cwd={full_game_path_from_config}{RESET}")
        subprocess.run(start_game_command, check=True, cwd=full_game_path_from_config)
        print(f"{GREEN}Příkaz '{start_game_command}' byl úspěšně spuštěn.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Chyba při spouštění příkazu '{start_game_command}': {e}{RESET}")
        print(f"{CYAN}DEBUG: Návratový kód chyby: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}{RESET}")
    except FileNotFoundError:
        print(f"{RED}Soubor '{start_game_command}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.{RESET}")
        print(f"{CYAN}DEBUG: Cesta k souboru, který nebyl nalezen: {start_game_command}{RESET}")
    except Exception as e:
        print(f"{RED}Nastala neočekávaná chyba při spouštění příkazu: {e}{RESET}")
        print(f"{CYAN}DEBUG: Typ chyby: {type(e).__name__}{RESET}")

else:
    print(f"{YELLOW}Verze hry není aktuální. Stahuji aktualizaci.{RESET}")
    print(f"{CYAN}DEBUG: Aktualizuji config['game_version'] z {config['game_version']} na {github_game_ver}.{RESET}")
    config["game_version"] = github_game_ver
    save_config(CONFIG_FILE, config)
    print(f"{GREEN}Nová verze uložena do config.json.{RESET}")

    # URL pro stažení aktualizace hry
    url_seznam_souboru = f"https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/{github_game_ver}/list.txt"
    print(f"{CYAN}DEBUG: URL pro seznam souborů aktualizace: {url_seznam_souboru}{RESET}")

    # Složka, kam se stáhne samotný soubor list.txt (aktuální složka)
    slozka_pro_stahovani_seznamu = os.path.join(os.getcwd(), "download")
    print(f"{CYAN}DEBUG: Složka pro stahování seznamu: {slozka_pro_stahovani_seznamu}{RESET}")

    # Název, pod kterým se lokálně uloží stažený seznam URL
    nazev_lokalniho_seznamu = "list.txt"
    print(f"{CYAN}DEBUG: Název lokálního seznamu: {nazev_lokalniho_seznamu}{RESET}")

    # Cílová složka pro soubory, které jsou uvedeny v list.txt
    slozka_pro_stahovani_obsahu_seznamu = os.path.join(os.getcwd(), "download")
    print(f"{CYAN}DEBUG: Složka pro stahování obsahu seznamu: {slozka_pro_stahovani_obsahu_seznamu}{RESET}")

    # Před stažením list.txt zajistíme, že složka pro stahování existuje
    if not os.path.exists(slozka_pro_stahovani_seznamu):
        os.makedirs(slozka_pro_stahovani_seznamu)
        print(f"{GREEN}Složka '{slozka_pro_stahovani_seznamu}' byla vytvořena pro uložení list.txt.{RESET}")

    print(f"{BLUE}Stahuji soubor se seznamem URL z: {url_seznam_souboru}{RESET}")
    list_txt_stazen_uspesne = False
    try:
        print(f"{CYAN}DEBUG: Pokouším se stáhnout list.txt z {url_seznam_souboru}{RESET}")
        cesta_k_lokalnimu_seznamu = os.path.join(slozka_pro_stahovani_seznamu, nazev_lokalniho_seznamu)
        download_file_with_progress(url_seznam_souboru, cesta_k_lokalnimu_seznamu)
        print(f"{GREEN}Seznam URL úspěšně stažen do: {cesta_k_lokalnimu_seznamu}{RESET}")
        list_txt_stazen_uspesne = True

    except requests.exceptions.RequestException as e:
        print(f"{RED}Chyba při stahování seznamu URL z GitHubu: {e}{RESET}")
        print(f"{CYAN}DEBUG: Detaily chyby RequestException: {e}{RESET}")
    except Exception as e:
        print(f"{RED}Nastala neočekávaná chyba: {e}{RESET}")
        print(f"{CYAN}DEBUG: Typ neočekávané chyby: {type(e).__name__}{RESET}")

    # Voláme update1 pouze pokud byl list.txt úspěšně stažen
    if list_txt_stazen_uspesne:
        print(f"{BLUE}Spouštím aktualizaci souborů...{RESET}")
        print(f"{CYAN}DEBUG: Volám funkci update1 s '{cesta_k_lokalnimu_seznamu}' a '{slozka_pro_stahovani_obsahu_seznamu}'.{RESET}")
        update1(cesta_k_lokalnimu_seznamu, slozka_pro_stahovani_obsahu_seznamu)
        print(f"{GREEN}Funkce update1 dokončena.{RESET}")

        print(f"{BLUE}Mažu dočasný soubor se seznamem URL...{RESET}")
        print(f"{CYAN}DEBUG: Pokouším se smazat soubor: {cesta_k_lokalnimu_seznamu}{RESET}")
        try:
            os.remove(cesta_k_lokalnimu_seznamu)
            print(f"{GREEN}Soubor '{nazev_lokalniho_seznamu}' byl úspěšně smazán.{RESET}")
        except OSError as e:
            print(f"{RED}Chyba při mazání souboru '{nazev_lokalniho_seznamu}': {e}{RESET}")
            print(f"{CYAN}DEBUG: Chyba OS při mazání: {e.strerror}{RESET}")
    else:
        print(f"{YELLOW}list.txt nebyl úspěšně stažen, přeskočím volání update1.{RESET}")


    if platform.system() == "Windows":
        start_command = ["cmd.exe", "/C", ".\\update.cmd", os.path.normpath(config['path_game'])]
        print(f"{CYAN}DEBUG: Systém je Windows, start_command pro aktualizaci nastaven na: {start_command}{RESET}")
    else: # Předpokládáme Linux nebo macOS
        start_command = ["./update.sh", os.path.normpath(config['path_game'])]
        print(f"{CYAN}DEBUG: Systém není Windows, start_command pro aktualizaci nastaven na: {start_command}{RESET}")

    print(f"{YELLOW}Spouštím příkaz pro aktualizaci: {start_command}{RESET}")
    try:
        subprocess.run(start_command, check=True, cwd=os.getcwd())
        print(f"{GREEN}Příkaz '{start_command}' pro aktualizaci byl úspěšně spuštěn.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Chyba při spouštění příkazu '{start_command}': {e}{RESET}")
        print(f"{CYAN}DEBUG: Návratový kód chyby aktualizace: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}{RESET}")
    except FileNotFoundError:
        # Použijeme index 2 pro Windows (cmd.exe /C SCRIPT) a index 0 pro Linux/macOS (SCRIPT)
        script_to_find = start_command[2] if platform.system() == 'Windows' and len(start_command) > 2 else start_command[0]
        print(f"{RED}Soubor '{script_to_find}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.{RESET}")
        print(f"{CYAN}DEBUG: Cesta k souboru aktualizace, který nebyl nalezen: {start_command}{RESET}")
    except Exception as e:
        print(f"{RED}Nastala neočekávaná chyba při spouštění příkazu: {e}{RESET}")
        print(f"{CYAN}DEBUG: Typ chyby při spouštění aktualizace: {type(e).__name__}{RESET}")

    # Po dokončení aktualizace externím skriptem se spustí hra
    if platform.system() == "Windows":
        start_game_command = ["cmd.exe", "/C", "run.bat"]
        print(f"{CYAN}DEBUG: Systém je Windows, start_game_command po aktualizaci nastaven na: {start_game_command}{RESET}")
    else: # Předpokládáme Linux nebo macOS
        start_game_command = "./run.sh"
        print(f"{CYAN}DEBUG: Systém není Windows, start_game_command po aktualizaci nastaven na: {start_game_command}{RESET}")

    print(f"{YELLOW}Spouštím hru: {start_game_command} v adresáři: {full_game_path_from_config}{RESET}")
    try:
        print(f"{CYAN}DEBUG: Pokouším se spustit subprocess pro hru po aktualizaci: {start_game_command}{RESET}")
        subprocess.run(start_game_command, check=True, cwd=full_game_path_from_config)
        print(f"{GREEN}Příkaz '{start_game_command}' po aktualizaci byl úspěšně spuštěn.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}Chyba při spouštění hry '{start_game_command}' po aktualizaci: {e}{RESET}")
        print(f"{CYAN}DEBUG: Návratový kód chyby hry po aktualizaci: {e.returncode}, Výstup: {e.output}, Chyba: {e.stderr}{RESET}")
    except FileNotFoundError:
        print(f"{RED}Soubor '{start_game_command[2] if platform.system() == 'Windows' else start_game_command[0]}' nebyl nalezen. Ujistěte se, že cesta je správná a soubor existuje.{RESET}")
        print(f"{CYAN}DEBUG: Cesta k souboru hry po aktualizaci, který nebyl nalezen: {start_game_command}{RESET}")
    except Exception as e:
        print(f"{RED}Nastala neočekávaná chyba při spouštění hry po aktualizaci: {e}{RESET}")
        print(f"{CYAN}DEBUG: Typ chyby hry po aktualizaci: {type(e).__name__}{RESET}")

# Důležité: Před ukončením programu obnovíme původní sys.stdout a zavřeme logovací soubor.
if isinstance(sys.stdout, Logger):
    log_file_path_for_message = sys.stdout.log_file_path
    if sys.stdout.log:
        sys.stdout.log.close()
    sys.stdout = sys.stdout._original_stdout
    if log_file_path_for_message:
        print(f"Logovací soubor '{log_file_path_for_message}' byl uzavřen.")
    else:
        print("Logovací soubor nebyl vytvořen kvůli chybě.")
