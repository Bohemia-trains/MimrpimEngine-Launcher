# -*- coding: utf-8 -*-
import subprocess
import os
import json
import platform
import sys # Import sys pro get_application_root

# Importujeme funkce pro správu konfigurace a zjištění kořenového adresáře
from funcions_own import get_application_root, load_config, save_config

# --- Nastavení aktuálního pracovního adresáře na kořen aplikace ---
# Tato část kódu je klíčová pro zajištění, že skript vždy pracuje
# z kořenového adresáře aplikace, bez ohledu na to, odkud byl spuštěn.
puvodni_cwd = os.getcwd()
print(f"Původní aktuální pracovní adresář (CWD): {puvodni_cwd}")

aplikacni_koren = get_application_root()
print(f"Zjištěný kořenový adresář aplikace (kde je skript/exe): {aplikacni_koren}")

try:
    os.chdir(aplikacni_koren)
    print(f"Aktuální pracovní adresář (CWD) změněn na: {os.getcwd()}")
except Exception as e:
    print(f"Chyba při změně adresáře na {aplikacni_koren}: {e}")

print("\n--- Pokračování updater.py ---")
print(f"Updater nyní pracuje v adresáři: {os.getcwd()}")

def run_updater():
    """
    Načte konfiguraci a spustí update.cmd/update.sh s parametry.
    """
    print("Spouštím run_updater.py...")

    # Cesty k souborům config.json a update skriptům se nyní odvozují
    # od aktuálního pracovního adresáře (který je již kořenem aplikace).
    CONFIG_DIR = os.path.join(os.getcwd(), "config")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    # Načtení konfigurace pomocí univerzální funkce z funcions_own.py
    config = load_config(CONFIG_FILE)

    # Získání parametrů z konfigurace
    path_game = config.get("path_game", "Game/")
    platform_version = config.get("platform_version", "Win64")

    # Sestavení absolutní cesty ke hře
    # Jelikož CWD je kořen aplikace, path_game by měla být relativní k němu
    absolute_path_game = os.path.join(os.getcwd(), path_game)

    # Normalizace cesty pro konzistentní formát
    normalized_path_game = os.path.normpath(absolute_path_game)

    print(f"Načtená path_game: {normalized_path_game}")
    print(f"Načtená platform_version: {platform_version}")

    updater_script = ""
    command_list = []

    if platform.system() == "Windows":
        updater_script = "update.bat"
        # Cesta k updater_script se odvozuje od aktuálního CWD
        full_updater_script_path = os.path.join(os.getcwd(), updater_script)
        
        # Klíčová změna: Pro shell=True předáme jeden řetězec,
        # kde jsou cesty správně uvozeny.
        # Použijeme 'call' pro spuštění bat souboru z jiného bat souboru/skriptu.
        command_string = f'call "{full_updater_script_path}" "{normalized_path_game}" "{platform_version}"'
        command_list = [command_string] # Nyní je to jeden řetězec
    else: # Předpokládáme Linux nebo macOS
        updater_script = "update.sh"
        # Cesta k updater_script se odvozuje od aktuálního CWD
        full_updater_script_path = os.path.join(os.getcwd(), updater_script)
        # Pro bash skripty je obvykle lepší předávat argumenty jako samostatné položky v seznamu,
        # ale zajistit, aby byly správně obaleny uvozovkami, pokud obsahují mezery.
        command_list = ["bash", full_updater_script_path, normalized_path_game, platform_version]
        # Zde normalized_path_game a platform_version by měly být předány bez extra uvozovek,
        # protože bash je bude interpretovat jako samostatné argumenty.
        # Pokud by cesty na Linuxu obsahovaly mezery a bylo by potřeba je obalit,
        # pak by se použilo f'"{normalized_path_game}"'. Pro jednoduchost to nechávám bez.

    print(f"Spouštím příkaz: {command_list}")
    try:
        # Spustí příkaz. check=True zajistí, že se vyvolá CalledProcessError, pokud příkaz selže.
        # cwd je nastaven na aktuální pracovní adresář (kořen aplikace),
        # aby se updater_script našel, pokud je přímo v kořeni.
        # Pro Windows a příkaz s cmd.exe /C je důležité použít shell=True.
        subprocess.run(command_list, check=True, cwd=os.getcwd(), shell=True if platform.system() == "Windows" else False)
        print(f"Příkaz '{' '.join(command_list)}' byl úspěšně spuštěn.")
    except FileNotFoundError:
        print(f"Chyba: Aktualizační skript '{updater_script}' nebyl nalezen v '{os.getcwd()}'.")
        print("Ujistěte se, že soubor existuje a je spustitelný.")
    except subprocess.CalledProcessError as e:
        print(f"Chyba při spouštění aktualizačního skriptu: {e}")
        print(f"Návratový kód: {e.returncode}")
        if e.stdout:
            print(f"Standardní výstup: {e.stdout.decode(errors='ignore')}") # Přidáno errors='ignore' pro dekódování
        if e.stderr:
            print(f"Standardní chyba: {e.stderr.decode(errors='ignore')}") # Přidáno errors='ignore' pro dekódování
    except Exception as e:
        print(f"Nastala neočekávaná chyba: {e}")

if __name__ == "__main__":
    run_updater()
