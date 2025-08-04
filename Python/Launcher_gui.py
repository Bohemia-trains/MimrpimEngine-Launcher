import tkinter as tk
from tkinter import scrolledtext
import subprocess
import sys
import requests
import markdown
from html.parser import HTMLParser
import json
import os
# Importujeme všechny potřebné funkce a třídu Logger z funcions_own
from funcions_own import Logger, get_application_root, save_config, load_config

# Konstanty pro barvy (zopakované zde pro přímé použití v tomto souboru)
RESET = "\033[0m"
RED = "\033[31m"      # Pro chyby
GREEN = "\033[32m"    # Pro úspěšné operace, dokončení
YELLOW = "\033[33m"   # Pro varování, uživatelský vstup, důležité informace
BLUE = "\033[34m"     # Pro obecné informace, úvodní zprávy
CYAN = "\033[36m"     # Pro debugovací zprávy
GREY = "\033[90m"     # Pro méně důležité, "tiché" zprávy

# --- Nastavení logování do souboru pro GUI ---
# Přesměrujeme sys.stdout na naši instanci Loggeru s příponou "_gui-launcher"
sys.stdout = Logger(log_suffix="_gui-launcher")


version = "1.0.1"
# --- Nastavení aktuálního pracovního adresáře na kořen aplikace ---
# Tuto část kódu je klíčové mít na začátku souboru,
# aby se aktuální pracovní adresář nastavil před jakýmikoli dalšími operacemi s cestami.
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


class MarkdownToTkinterParser(HTMLParser):
    """
    Vlastní HTML parser, který převádí HTML tagy na Tkinter tagy
    a vkládá text do scrolledtext widgetu.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.current_tags = []

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.text_widget.insert(tk.END, "\n")
            self.current_tags.append("h1")
        elif tag == "h2":
            self.text_widget.insert(tk.END, "\n")
            self.current_tags.append("h2")
        elif tag == "p":
            self.text_widget.insert(tk.END, "\n")
            self.current_tags.append("paragraph")
        elif tag == "strong":
            self.current_tags.append("bold")
        elif tag == "em":
            self.current_tags.append("italic")

    def handle_endtag(self, tag):
        if tag == "h1" and "h1" in self.current_tags:
            self.current_tags.remove("h1")
            self.text_widget.insert(tk.END, "\n")
        elif tag == "h2" and "h2" in self.current_tags:
            self.current_tags.remove("h2")
            self.text_widget.insert(tk.END, "\n")
        elif tag == "p" and "paragraph" in self.current_tags:
            self.current_tags.remove("paragraph")
            self.text_widget.insert(tk.END, "\n")
        elif tag == "strong" and "bold" in self.current_tags:
            self.current_tags.remove("bold")
        elif tag == "em" and "italic" in self.current_tags:
            self.current_tags.remove("italic")

    def handle_data(self, data):
        if self.current_tags:
            self.text_widget.insert(tk.END, data, tuple(self.current_tags))
        else:
            self.text_widget.insert(tk.END, data)

def run_game(force_install_var, config):
    """
    Zavře okno GUI a spustí externí příkaz v závislosti na stavu checkboxu.
    Spustitelné soubory (force_start.exe, Launcher.exe) se hledají ve stejném adresáři jako skript.
    """
    root.destroy()  # Zavře hlavní okno
    try:
        # Použijeme aktuální pracovní adresář, který už byl nastaven na kořen aplikace
        current_app_root = os.getcwd()

        # Získá cestu ke hře z konfigurace
        path_game = config.get("path_game", "Game/")

        # Sestaví celou cestu k adresáři hry
        full_game_path = os.path.join(current_app_root, path_game)

        # Vytvoří složku path_game, pokud neexistuje
        if not os.path.exists(full_game_path):
            os.makedirs(full_game_path)
            print(f"{GREEN}Vytvořena složka pro hru: {full_game_path}{RESET}")

        if force_install_var.get():
            executable_name = "force_start.exe"
        else:
            executable_name = "Launcher.exe"

        # Sestaví celou cestu k spustitelnému souboru ve stejném adresáři
        full_command_path = os.path.join(current_app_root, executable_name)

        # Použití uvozovek pro cesty s mezerami
        print(f"{BLUE}Spouštím externí příkaz: {full_command_path}{RESET}")
        subprocess.Popen(f"start \"\" \"{full_command_path}\"", shell=True)
    except Exception as e:
        print(f"{RED}Chyba při spouštění příkazu: {e}{RESET}")

def fetch_changelog_content(url):
    """
    Načte obsah souboru z dané URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"{RED}Chyba při načítání obsahu changelogu z {url}: {e}{RESET}")
        return f"Chyba při načítání obsahu: {e}\nZkontrolujte připojení k internetu nebo URL."

def fetch_remote_game_version(url):
    """
    Načte vzdálenou verzi hry z dané URL.
    Vrací verzi jako řetězec nebo None v případě chyby.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"{RED}Chyba při načítání vzdálené verze z {url}: {e}{RESET}")
        return None

def apply_markdown_to_text_widget(text_widget, md_content):
    """
    Konvertuje Markdown obsah na HTML a aplikuje základní formátování
    na textový widget pomocí vlastního HTML parseru.
    """
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)

    text_widget.tag_configure("h1", font=("Arial", 16, "bold"))
    text_widget.tag_configure("h2", font=("Arial", 14, "bold"))
    text_widget.tag_configure("bold", font=("Arial", 10, "bold"))
    text_widget.tag_configure("italic", font=("Arial", 10, "italic"))
    text_widget.tag_configure("paragraph", font=("Arial", 10))

    html_content = markdown.markdown(md_content)

    parser = MarkdownToTkinterParser(text_widget)
    parser.feed(html_content)
    parser.close()

    text_widget.config(state=tk.DISABLED)

def open_settings_window(config_file_path, current_config):
    """
    Otevře nové okno pro nastavení, kde lze upravit cestu ke hře.
    """
    settings_window = tk.Toplevel(root)
    settings_window.title("Nastavení launcheru")
    settings_window.geometry("450x150")
    settings_window.configure(bg="white")

    settings_window.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (settings_window.winfo_width() // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (settings_window.winfo_height() // 2)
    settings_window.geometry(f"+{x}+{y}")

    tk.Label(settings_window, text="Cesta ke hře:", bg="white", fg="black", font=("Arial", 10)).pack(pady=5)

    path_game_var = tk.StringVar(value=current_config.get("path_game", "Game/"))
    path_game_entry = tk.Entry(settings_window, textvariable=path_game_var, width=50)
    path_game_entry.pack(pady=5)

    def save_and_close_settings():
        new_path_game = path_game_var.get()
        current_config["path_game"] = new_path_game
        save_config(config_file_path, current_config) # Použijeme importovanou save_config
        print(f"{GREEN}Cesta ke hře uložena: {new_path_game}{RESET}")
        settings_window.destroy()

    button_frame = tk.Frame(settings_window, bg="white")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Uložit", command=save_and_close_settings).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Zrušit", command=settings_window.destroy).pack(side=tk.RIGHT, padx=5)

    settings_window.grab_set()
    root.wait_window(settings_window)

def check_version_and_update_button(play_button_text_var, force_install_var, config):
    """
    Fetches remote game version, compares it with local config,
    and updates the Play/Install button text.
    """
    local_version = config.get("game_version", "0.0.0").strip()
    remote_version_url = "https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/game.version"
    remote_version = fetch_remote_game_version(remote_version_url)

    print(f"{BLUE}Kontroluji verzi hry... Lokální: {local_version}, Vzdálená: {remote_version}{RESET}")

    if force_install_var.get():
        play_button_text_var.set("Install (Force)")
        print(f"{YELLOW}Force Install je aktivní. Tlačítko nastaveno na 'Install (Force)'.{RESET}")
    elif (remote_version is None) or (local_version != remote_version):
        play_button_text_var.set("Install")
        if remote_version is None:
            print(f"{YELLOW}Nelze načíst vzdálenou verzi. Tlačítko nastaveno na 'Install'.{RESET}")
        else:
            print(f"{YELLOW}Verze hry není aktuální. Tlačítko nastaveno na 'Install'.{RESET}")
    else:
        play_button_text_var.set("Play")
        print(f"{GREEN}Verze hry je aktuální. Tlačítko nastaveno na 'Play'.{RESET}")

def on_platform_version_change(platform_version_var, config, config_file_path):
    """
    Called when the platform version selection changes.
    Updates the config and saves it.
    """
    selected_version = platform_version_var.get()
    config["platform_version"] = selected_version
    save_config(config_file_path, config) # Použijeme importovanou save_config
    print(f"{BLUE}Platform version changed to: {selected_version}{RESET}")


def create_gui():
    """
    Vytvoří a nakonfiguruje GUI okno.
    """
    global root
    root = tk.Tk()

    # Získá aktuální pracovní adresář, který už byl nastaven na kořen aplikace
    current_app_root = os.getcwd()

    config_dir_path = os.path.join(current_app_root, "config")
    config_file_path = os.path.join(config_dir_path, "config.json")

    # Vytvoří složku config, pokud neexistuje
    if not os.path.exists(config_dir_path):
        os.makedirs(config_dir_path)
        print(f"{GREEN}Vytvořena složka pro konfiguraci: {config_dir_path}{RESET}")

    config = load_config(config_file_path) # Použijeme importovanou load_config
    print(f"{BLUE}Konfigurace načtena: {config}{RESET}")

    # Nastavení ikony okna
    # Nyní používáme current_app_root, který je kořenem aplikace
    icon_path = os.path.join(current_app_root, "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
            print(f"{GREEN}Ikona okna načtena z: {icon_path}{RESET}")
        except tk.TclError as e:
            print(f"{RED}Chyba při načítání ikony: {e}. Ujistěte se, že soubor 'icon.ico' je platný formát ICO.{RESET}")
    else:
        print(f"{YELLOW}Soubor ikony '{icon_path}' nebyl nalezen.{RESET}")

    root.title("MimrpimEngine Launcher - Version " + version)

    window_width = 854
    window_height = 480

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)

    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    root.configure(bg="white")

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)

    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=0)
    root.grid_columnconfigure(2, weight=1)
    root.grid_columnconfigure(3, weight=0)
    root.grid_columnconfigure(4, weight=0) # Changed from 1 to 0 for right_controls_group_frame
    root.grid_columnconfigure(5, weight=0)
    root.grid_columnconfigure(6, weight=1)


    text_area = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        width=40,
        height=10,
        bg="white",
        fg="black",
        font=("Arial", 10),
        relief="solid",
        borderwidth=2
    )
    text_area.grid(row=0, column=0, columnspan=7, padx=20, pady=20, sticky="nsew")

    changelog_url = "https://raw.githubusercontent.com/Bohemia-trains/MimrpimEngine-Download/refs/heads/main/launcher/changelog.md"

    print(f"{BLUE}Načítám obsah changelogu z: {changelog_url}{RESET}")
    changelog_content = fetch_changelog_content(changelog_url)
    print(f"{GREEN}Changelog načten.{RESET}")

    apply_markdown_to_text_widget(text_area, changelog_content)

    controls_frame = tk.Frame(root, bg="white")
    controls_frame.grid(row=1, column=0, columnspan=7, pady=10, sticky="ew")

    controls_frame.grid_columnconfigure(0, weight=0)
    controls_frame.grid_columnconfigure(1, weight=1)
    controls_frame.grid_columnconfigure(2, weight=0)
    controls_frame.grid_columnconfigure(3, weight=1)
    controls_frame.grid_columnconfigure(4, weight=0)


    left_controls_group_frame = tk.Frame(controls_frame, bg="white")
    left_controls_group_frame.grid(row=0, column=0, sticky="w")

    left_controls_group_frame.grid_columnconfigure(0, weight=0)
    left_controls_group_frame.grid_columnconfigure(1, weight=0)

    force_install_var = tk.BooleanVar()

    settings_button = tk.Button(
        left_controls_group_frame,
        text="Nastavení",
        command=lambda: open_settings_window(config_file_path, config)
    )
    settings_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    print(f"{BLUE}Tlačítko 'Nastavení' vytvořeno.{RESET}")

    force_install_checkbox = tk.Checkbutton(
        left_controls_group_frame,
        text="Force Install",
        variable=force_install_var,
        bg="white",
        fg="black",
        font=("Arial", 10)
    )
    force_install_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    print(f"{BLUE}Checkbox 'Force Install' vytvořen.{RESET}")

    play_button_text_var = tk.StringVar()

    play_button = tk.Button(
        controls_frame,
        textvariable=play_button_text_var,
        command=lambda: run_game(force_install_var, config)
    )
    play_button.grid(row=0, column=2, padx=10, pady=5)
    print(f"{BLUE}Tlačítko Play/Install vytvořeno.{RESET}")

    force_install_var.trace_add("write", lambda *args: check_version_and_update_button(play_button_text_var, force_install_var, config))

    right_controls_group_frame = tk.Frame(controls_frame, bg="white")
    right_controls_group_frame.grid(row=0, column=4, sticky="e")

    right_controls_group_frame.grid_columnconfigure(0, weight=0)
    right_controls_group_frame.grid_columnconfigure(1, weight=0)

    platform_options = ["Win64", "Win32", "WinARM", "Linux64", "LinuxARM32", "LinuxARM64"]
    platform_version_var = tk.StringVar(root)
    platform_version_var.set(config.get("platform_version", platform_options[0]))

    platform_label = tk.Label(right_controls_group_frame, text="Vyberte verzi:", bg="white", fg="black", font=("Arial", 10))
    platform_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    print(f"{BLUE}Popisek 'Vyberte verzi:' vytvořen.{RESET}")

    platform_dropdown = tk.OptionMenu(
        right_controls_group_frame,
        platform_version_var,
        *platform_options,
        command=lambda x: on_platform_version_change(platform_version_var, config, config_file_path)
    )
    platform_dropdown.config(bg="white", fg="black", font=("Arial", 10))
    platform_dropdown["menu"].config(bg="white", fg="black", font=("Arial", 10))
    platform_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    print(f"{BLUE}Dropdown pro výběr platformy vytvořen.{RESET}")

    check_version_and_update_button(play_button_text_var, force_install_var, config)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
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
