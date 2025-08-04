# funcions_own.py
import os
import requests
from urllib.parse import urlparse
import json
import sys
import datetime # Pro Logger
from tqdm import tqdm # pyright: ignore[reportMissingModuleSource] # Pro download_file_with_progress
import re # Import pro regulární výrazy pro odstranění barevných kódů
import zipfile # Pro kompresi logů
import glob # Pro hledání souborů

# Konstanty pro barvy (OPRAVENO: RED bylo "\031m", má být "\033[31m")
RESET = "\033[0m"
RED = "\033[31m"      # Pro chyby
GREEN = "\033[32m"    # Pro úspěšné operace, dokončení
YELLOW = "\033[33m"   # Pro varování, uživatelský vstup, důležité informace
BLUE = "\033[34m"     # Pro obecné informace, úvodní zprávy
CYAN = "\033[36m"     # Pro debugovací zprávy
GREY = "\033[90m"     # Pro méně důležité, "tiché" zprávy
# První print pro ověření, že se soubor načítá
print (f"{BLUE}-=- Funcions Own -=-{RESET}")

# Počet dní, po kterých budou logy komprimovány a archivovány
# Pokud je nastaveno na 0, archivují se všechny logy kromě aktuálně otevřeného.
# Pro produkci zvažte vyšší číslo (např. 7).
LOG_RETENTION_DAYS = 7 

# --- Třída pro logování do souboru a terminálu ---
class Logger(object):
    def __init__(self, log_suffix="_console-launcher"):
        self.terminal = sys.stdout # Uložíme původní standardní výstup (konzoli)
        self._original_stdout = sys.stdout # Reference na původní stdout pro obnovení
        self.log_suffix = log_suffix # Uložíme příponu pro název logu (např. "_console-launcher" nebo "_gui-launcher")
        self.log = None # Inicializujeme self.log na None, dokud není soubor úspěšně otevřen
        self.log_file_path = None # Cesta k logovacímu souboru
        self.is_initialized_successfully = False # Nový příznak pro úspěšnou inicializaci

        # Vytvoření názvu souboru s datem a časem pro aktuální log
        now_init = datetime.datetime.now()
        log_filename = now_init.strftime(f"%d-%m-%Y-%H-%M-%S{self.log_suffix}.log")

        # Cesta ke složce logs/ (relativní k aktuálnímu pracovnímu adresáři)
        self.log_dir = os.path.join(os.getcwd(), "logs")
        
        # Zajištění, že složka logs/ existuje
        try:
            if not os.path.exists(self.log_dir):
                os.makedirs(self.log_dir)
                self.terminal.write(f"{GREEN}Vytvořena složka pro logy: '{self.log_dir}'{RESET}\n")
        except Exception as e:
            self.terminal.write(f"{RED}Chyba při vytváření složky pro logy '{self.log_dir}': {e}{RESET}\n")
            # Pokud se nepodaří vytvořit složku, logovací soubor se neotevře
            # is_initialized_successfully zůstane False
            # Není zde 'return', aby se kód pokusil pokračovat a self.log zůstalo None
            return # Zde se inicializace přeruší, ale self.terminal je stále původní stdout

        # Sestavení kompletní cesty k logovacímu souboru
        self.log_file_path = os.path.join(self.log_dir, log_filename)
        
        try:
            self.log = open(self.log_file_path, "a", encoding="utf-8")
            self.terminal.write(f"{BLUE}Logování přesměrováno do souboru: '{self.log_file_path}'{RESET}\n")
            self.is_initialized_successfully = True # Úspěšná inicializace
            # Po inicializaci nového logu zkomprimujeme a archivujeme staré logy
            self._compress_and_archive_old_logs()
        except Exception as e:
            self.terminal.write(f"{RED}Chyba při otevírání logovacího souboru '{self.log_file_path}': {e}{RESET}\n")
            self.log = None # Zajistíme, že self.log je None, pokud se soubor neotevře
            self.is_initialized_successfully = False # Inicializace selhala


    def write(self, message):
        self.terminal.write(message) # Zapisujeme do konzole (s barvami)
        # Zapisujeme do souboru pouze, pokud self.log není None a soubor není uzavřen
        if self.log and not self.log.closed:
            # Odstranění ANSI escape kódů před zápisem do souboru
            clean_message = re.sub(r'\x1b\[[0-9;]*m', '', message)
            self.log.write(clean_message)

    def flush(self):
        self.terminal.flush()
        # Vyprázdnění souboru pouze, pokud self.log není None a soubor není uzavřen
        if self.log and not self.log.closed:
            self.log.flush()

    def _compress_and_archive_old_logs(self):
        """
        Komprimuje a archivuje logy starší než LOG_RETENTION_DAYS.
        Archivované logy jsou přesunuty do podsložky 'archive' v adresáři 'logs/'.
        Název archivu odráží datumový rozsah logů v něm obsažených (z názvů souborů).
        Archivuje pouze logy s příponou odpovídající self.log_suffix.
        """
        # Získání aktuálního času pro porovnání stáří logů (z modifikace souboru)
        now = datetime.datetime.now() 

        self.terminal.write(f"{BLUE}Kontroluji staré logy pro archivaci (starší než {LOG_RETENTION_DAYS} dní)...{RESET}\n")
        archive_dir = os.path.join(self.log_dir, "archive")
        
        try:
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir)
                self.terminal.write(f"{GREEN}Vytvořena složka pro archivaci logů: '{archive_dir}'{RESET}\n")
        except Exception as e:
            self.terminal.write(f"{RED}Chyba při vytváření složky pro archivaci '{archive_dir}': {e}{RESET}\n")
            return

        # Získání seznamu všech log souborů v log_dir, kromě aktuálního
        log_files_to_archive = []
        earliest_log_datetime = None
        latest_log_datetime = None
        earliest_log_filename = None # To store the actual filename string
        latest_log_filename = None   # To store the actual filename string

        # Regex pro extrakci CELÉHO DATUMU A ČASU z názvu souboru s dynamickou příponou
        # Zachytí dd-mm-yyyy-hh-mm-ss a použije re.escape pro správné ošetření speciálních znaků v příponě
        timestamp_pattern = re.compile(rf'(\d{{2}}-\d{{2}}-\d{{4}}-\d{{2}}-\d{{2}}-\d{{2}}){re.escape(self.log_suffix)}\.log')

        for log_file_path in glob.glob(os.path.join(self.log_dir, "*.log")):
            # Zajistíme, že nearchivujeme právě otevřený logovací soubor
            if os.path.abspath(log_file_path) != os.path.abspath(self.log_file_path):
                filename = os.path.basename(log_file_path)
                
                # Kontrola, zda název souboru končí na očekávanou příponu
                if not filename.endswith(f"{self.log_suffix}.log"):
                    self.terminal.write(f"{GREY}Přeskakuji log '{filename}' - nemá příponu '{self.log_suffix}.log'.{RESET}\n")
                    continue

                mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(log_file_path))
                
                # Upravená podmínka pro archivaci (stále používá mod_time)
                if LOG_RETENTION_DAYS == 0 or (now - mod_time).days > LOG_RETENTION_DAYS:
                    
                    # Pokus o extrakci data a času z názvu souboru
                    match = timestamp_pattern.match(filename)
                    
                    if match:
                        timestamp_str_from_filename = match.group(1) # Získá "dd-mm-yyyy-hh-mm-ss"
                        try:
                            parsed_dt = datetime.datetime.strptime(timestamp_str_from_filename, "%d-%m-%Y-%H-%M-%S")
                            
                            log_files_to_archive.append(log_file_path)
                            
                            # Aktualizace nejstaršího a nejnovějšího datetime objektu a jejich názvů souborů
                            if earliest_log_datetime is None or parsed_dt < earliest_log_datetime:
                                earliest_log_datetime = parsed_dt
                                earliest_log_filename = filename
                            if latest_log_datetime is None or parsed_dt > latest_log_datetime:
                                latest_log_datetime = parsed_dt
                                latest_log_filename = filename
                        except ValueError:
                            self.terminal.write(f"{YELLOW}Varování: Nelze parsovat datum a čas z názvu logu '{filename}'. Přeskakuji pro určení rozsahu názvu archivu.{RESET}\n")
                    else:
                        self.terminal.write(f"{YELLOW}Varování: Datum a čas v názvu logu '{filename}' neodpovídá očekávanému formátu (dd-mm-yyyy-hh-mm-ss). Přeskakuji pro určení rozsahu názvu archivu.{RESET}\n")

        if not log_files_to_archive:
            self.terminal.write(f"{BLUE}Nenalezeny žádné staré logy k archivaci.{RESET}\n")
            return

        # Vytvoření názvu pro archivní ZIP soubor s datumovým rozsahem
        if earliest_log_filename and latest_log_filename:
            if earliest_log_filename == latest_log_filename:
                archive_name = f"{earliest_log_filename}.zip"
            else:
                # Odstraníme příponu .log z názvů souborů pro název archivu
                earliest_log_filename_no_suffix = earliest_log_filename.replace(".log", "")
                latest_log_filename_no_suffix = latest_log_filename.replace(".log", "")
                archive_name = f"{earliest_log_filename_no_suffix}_-_{latest_log_filename_no_suffix}.zip"
        else:
            # Fallback, pokud by z nějakého důvodu nebyly nalezeny názvy souborů (nemělo by se stát, pokud log_files_to_archive není prázdné)
            archive_name = now.strftime("logs_archive_%Y-%m-%d_fallback.zip")

        archive_path = os.path.join(archive_dir, archive_name)

        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in log_files_to_archive:
                    arcname = os.path.basename(file_path)
                    zipf.write(file_path, arcname)
                    self.terminal.write(f"{GREEN}Archivován log: '{arcname}'{RESET}\n")
            
            # Smazání původních souborů po úspěšné archivaci
            for file_path in log_files_to_archive:
                os.remove(file_path)
                self.terminal.write(f"{GREEN}Smazán původní log: '{os.path.basename(file_path)}'{RESET}\n")
            
            self.terminal.write(f"{GREEN}Staré logy úspěšně archivovány do: '{archive_path}'{RESET}\n")

        except Exception as e:
            self.terminal.write(f"{RED}Chyba při archivaci logů: {e}{RESET}\n")


# --- Funkce pro zjištění kořenového adresáře aplikace ---
def get_application_root():
    """
    Vrátí absolutní cestu ke kořenovému adresáři aplikace.
    Funguje pro normální spuštění Python skriptu i pro PyInstaller balíčky (--onedir, --onefile).
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# --- Funkce pro ukládání konfigurace ---
def save_config(config_file_path, config_data):
    """
    Uloží konfigurační data do souboru JSON.
    """
    try:
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        print(f"{GREEN}Konfigurace úspěšně uložena do '{config_file_path}'.{RESET}")
    except Exception as e:
        print(f"{RED}Chyba při ukládání konfigurace: {e}{RESET}")

# --- Funkce pro načítání konfigurace ---
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
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
        return config
    except FileNotFoundError:
        print(f"{YELLOW}Chyba: Soubor '{config_file_path}' nebyl nalezen. Vytvářím výchozí konfiguraci.{RESET}")
        save_config(config_file_path, default_config)
        return default_config
    except json.JSONDecodeError:
        print(f"{RED}Chyba: Chybný formát JSON v souboru '{config_file_path}'. Používám výchozí konfiguraci.{RESET}")
        save_config(config_file_path, default_config)
        return default_config
    except Exception as e:
        print(f"{RED}Nastala neočekávaná chyba při načítání souboru '{config_file_path}': {e}{RESET}")
        save_config(config_file_path, default_config)
        return default_config

# --- Funkce pro stahování souborů s progress barem ---
def download_file_with_progress(url, filename):
    """
    Stáhne soubor z dané URL a zobrazí progress bar v konzoli s procenty dokončení.
    Zajistí, že cílový adresář existuje před stahováním.

    Args:
        url (str): URL adresa souboru, který se má stáhnout.
        filename (str): Název souboru, pod kterým se má stažený soubor uložit (včetně cesty).
    """
    target_dir = os.path.dirname(filename)
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        print(f"{CYAN}DEBUG: Vytvořena složka pro stahování: {target_dir}{RESET}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        block_size = 1024

        if total_size_in_bytes == 0:
            print(f"{YELLOW}Varování: Nelze zjistit celkovou velikost souboru '{os.path.basename(filename)}' z hlaviček. Progress bar nebude zobrazovat procenta dokončení.{RESET}")

        with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, desc=f"Stahuji {os.path.basename(filename)}") as progress_bar:
            with open(filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            print(f"\n{GREEN}Soubor '{os.path.basename(filename)}' byl úspěšně stažen.{RESET}")

    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"{RED}Chyba při stahování souboru '{os.path.basename(filename)}': {e}{RESET}")
    except Exception as e:
        raise Exception(f"{RED}Nastala neočekávaná chyba při stahování souboru '{os.path.basename(filename)}': {e}{RESET}")

# --- Funkce pro aktualizaci souborů ze seznamu URL ---
def update1(soubor_s_url: str, cilova_slozka: str):
    """
    Stáhne soubory z URL adres uvedených v textovém souboru
    a uloží je do zadané složky se zachováním původních názvů.
    Každý stahovaný soubor zobrazí svůj vlastní progress bar.

    Args:
        soubor_s_url (str): Cesta k textovému souboru, kde je na každém řádku 1 URL.
        cilova_slozka (str): Cesta k cílové složce, kam se soubory uloží.
    """
    if not os.path.exists(cilova_slozka):
        os.makedirs(cilova_slozka)
        print(f"{GREEN}Vytvořena složka: {cilova_slozka}{RESET}")

    try:
        with open(soubor_s_url, 'r', encoding='utf-8') as f:
            urls = f.readlines()
    except FileNotFoundError:
        print(f"{RED}Chyba: Soubor '{soubor_s_url}' s URL adresami nebyl nalezen.{RESET}")
        return

    stazeno_uspesne = 0
    stazeno_selhalo = 0

    print(f"{BLUE}Začínám stahování souborů do složky '{cilova_slozka}' z lokálního seznamu.{RESET}")

    for i, radek_url in enumerate(urls):
        url = radek_url.strip()
        if not url:
            continue

        try:
            parsed_url = urlparse(url)
            nazev_souboru = os.path.basename(parsed_url.path)

            if not nazev_souboru:
                print(f"{YELLOW}Upozornění: Nelze získat název souboru z URL: {url}. Přeskakuji toto URL.{RESET}")
                continue

            cesta_k_souboru = os.path.join(cilova_slozka, nazev_souboru)

            print(f"{CYAN}Stahuji soubor {i+1}/{len(urls)}: '{url}' do '{cesta_k_souboru}'...{RESET}")

            # Použijeme download_file_with_progress pro každý soubor v seznamu
            download_file_with_progress(url, cesta_k_souboru)

            stazeno_uspesne += 1

        except requests.exceptions.RequestException as e:
            print(f"{RED}Chyba při stahování {url}: {e}{RESET}")
            stazeno_selhalo += 1
        except Exception as e:
            print(f"{RED}Nastala neočekávaná chyba u {url}: {e}{RESET}")
            stazeno_selhalo += 1

    print(f"\n{BLUE}--- Stahování obsahu seznamu dokončeno ---{RESET}")
    print(f"{GREEN}Celkem staženo úspěšně: {stazeno_uspesne}{RESET}")
    print(f"{RED}Celkem selhalo: {stazeno_selhalo}{RESET}")
print(f"{BLUE}-=- End of Funcions Own -=-{RESET}")
