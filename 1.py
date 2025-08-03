import os
import sys

# --- Funkce pro zjištění kořenového adresáře aplikace ---

# --- Hlavní logika programu ---

# 1. Zjistíme původní aktuální pracovní adresář (kde jsme byli spuštěni)
puvodni_cwd = os.getcwd()
print(f"Původní aktuální pracovní adresář (CWD): {puvodni_cwd}")

# 2. Zjistíme skutečný kořenový adresář, kde je aplikace (skript/exe) fyzicky umístěna
aplikacni_koren = get_application_root()
print(f"Zjištěný kořenový adresář aplikace (kde je skript/exe): {aplikacni_koren}")

# 3. Změníme aktuální pracovní adresář (CWD) na kořenový adresář aplikace
# Tím zajistíme, že všechny relativní cesty (např. k datovým souborům, obrázkům)
# budou správně vyhodnoceny vzhledem k umístění aplikace, bez ohledu na to,
# odkud byl program spuštěn.
try:
    os.chdir(aplikacni_koren)
    print(f"Aktuální pracovní adresář (CWD) změněn na: {os.getcwd()}")
except Exception as e:
    print(f"Chyba při změně adresáře na {aplikacni_koren}: {e}")

# --- Původní logika uživatele (zamyšlení nad ní) ---
# Tvoje původní podmínka "if os.path.basename(os.getcwd()) == "_internal":"
# byla pravděpodobně zamýšlena pro situaci, kdy je tvůj hlavní skript
# uložen v podadresáři "_internal" a chceš, aby program pracoval
# z nadřazeného adresáře.

# Po změně CWD na "aplikacni_koren" už by tato podmínka neměla být potřeba
# nebo by se musela přehodnotit. Pokud tvůj program po zabalení očekává
# nějakou strukturu souborů vedle .exe, pak nastavení CWD na
# `aplikacni_koren` je obvykle vše, co potřebuješ.

# Příklad: Pokud máš soubor "data.txt" vedle "MujProgram.exe"
# v adresáři "dist/MujProgram/", pak ho můžeš otevřít takto:
# with open("data.txt", "r") as f:
#     obsah = f.read()
# print(f"\nObsah souboru data.txt (pokud existuje): {obsah}")

print("\n--- Pokračování programu ---")
print(f"Program nyní pracuje v adresáři: {os.getcwd()}")
# Zde pokračuje zbytek tvého programu, který bude používat relativní cesty
# vzhledem k adresáři, kde je tvůj spustitelný soubor.
