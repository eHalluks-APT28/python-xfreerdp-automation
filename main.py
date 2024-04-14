import os
import tty
import termios
import signal
import sys
import uuid
import getpass
import subprocess
class Computer:
    def __init__(self, name, ip):
        self.id = uuid.uuid4()
        self.name = name
        self.ip = ip

computers = []

# adjust as you need
comp1 = Computer("PC 1 - salon", "192.168.0.1")
comp2 = Computer("PC 2 - gabinet", "192.168.0.2")
comp3 = Computer("PC 3 - game room", "192.168.0.3")

computers.append(comp1)
computers.append(comp2)
computers.append(comp3)

availableConnections = ["Szybkie polaczenie", "Polaczenie zaawansowane", "Zakoncz dzialanie skryptu"]
availableScreenOptions = ["Jeden monitor", "Wszystkie monitory"]
universalYesNo = ["tak", "nie"]

# handle CTRL+C
def signal_handler(sig, frame):
    print("")
    print("\n Przerwano dzialanie skryptu za pomoca CTRL+C.\n")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def selectMovment(availableMovements):
    print("\n =================================================================")
    print("\n  Creator: ehalluks\n  Website: https://www.ehalluks.com/knowledge-base\n  Tool: xfreerdp\n  License: MIT\n  Version: 1.0.0\n")
    print("  Hot Keys:\n\n  >> CTRL+ALT+ENTER - Przelaczanie trybu fullscreen\n  >> CTRL+C - przerwanie dzialania skryptu\n")
    print(" =================================================================\n")
    print("\n Menu:\n")
    for index, movement in enumerate(availableMovements, start=1):
        print(f"  {index}.) - {movement}")

    choise = input("\n Wybierz dzialanie: ")
    return choise

menuSelection = selectMovment(availableConnections)

def selectPC(computers):
    for index, pc in enumerate(computers, start=1):
        print(f"    {index}.) - {pc.name}")
    choice = input("\n    Wybierz urządzenie: ")

    if choice.isdigit() and 1 <= int(choice) <= len(computers):
        selected_pc = computers[int(choice) - 1]
        return selected_pc

def get_password():
    print("    Wprowadź hasło: ", end="", flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        password = []
        while True:
            ch = sys.stdin.read(1)
            if ch in ['\n', '\r']:
                print("")
                break
            elif ch == '\x7f':  # Backspace
                if len(password) > 0:
                    password.pop()
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password.append(ch)
                sys.stdout.write('*')
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ''.join(password)

def get_screenMode(availableScreenOptions):
    print(" ")
    for index, option in enumerate(availableScreenOptions, start=1):
        print(f"    {index}.) - {option}")
    choise = input("\n    Wybierz tryb monitorow: ")
    return choise


def get_monitorNumber():
    print(" ")
    result = subprocess.run(['xfreerdp', '/monitor-list'], capture_output=True, text=True)
    print(result.stdout)
    print(" ")
    selectedMonitor = input("    Podaj numer monitora: ")
    return selectedMonitor

def isLanConfig(universalYesNo):
    print("\n    Czy chcesz ustawić LAN w konfiguracji sieci\n")
    for index, option in enumerate(universalYesNo, start=1):
        print(f"    {index}.) - {option}")
    choise = input("\n    Wybierz opcje: ")
    return choise

def get_usbMode():
    print("\n    Czy potrzebujesz udostepnic usb:\n")
    for index, option in enumerate(universalYesNo, start=1):
        print(f"    {index}.) - {option}")
    choise = input("\n    Wybierz opcje: ")
    return choise

def get_driveUsbData():
    print(" ")
    result = subprocess.run(['df', '-h'], capture_output=True, text=True)
    stdout_content = result.stdout
    indented_text = "\n".join(f"    {line}" for line in stdout_content.splitlines())
    print(indented_text)
    print(" ")
    driveName = "usb"
    drivePath = input("    Podaj sciezke do usb: ")

    return driveName, drivePath


def get_driveData():

    home_path = os.path.expanduser('~')
    username = os.getenv('USER')

    driveName = input("\n    Podaj nazwe dysku (unikaj nawiasow oraz spacji): ")

    print(f"\n    Nazwa twojego uzytkownika to: {username}")
    print("\n    Sciezka do Twojego katalogu domowego:", home_path)
    print("\n    Zawartosc katalogu domowego:\n")
    command = f"ls -d {home_path}/*/ --color=never"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    stdout_content = result.stdout
    indented_text = "\n".join(f"    {line}\n" for line in stdout_content.splitlines())
    print(indented_text)
    drivePath = input("    Podaj sciezke do folderu docelowego w twoim lokalnym systemie (unikaj znaku tylda): ")

    return driveName, drivePath


def get_defaultParameters():

    selected_computer = selectPC(computers)
    ip = selected_computer.ip
    windowCaption = f"'{selected_computer.name}'"
    monitor = get_screenMode(availableScreenOptions)
    login = input("\n    Wprowadz login: ")
    password = get_password()

    return ip, windowCaption, monitor, login, password

def createFastConnection():

    ip, windowCaption, monitor, login, password = get_defaultParameters()

    if monitor == "1":
        command = f"xfreerdp /v:{ip} /u:{login} /p:{password} /t:{windowCaption} /network:auto /rfx /gfx /compression /mouse-motion /dynamic-resolution /clipboard /sound"
    else:
        command = f"xfreerdp /v:{ip} /u:{login} /p:{password} /t:{windowCaption} /network:auto /rfx /gfx /compression /mouse-motion /multimon /clipboard /sound"

    runConnection(command, ip)


def createAdvancedConnection():

    ip, windowCaption, monitor, login, password = get_defaultParameters()

    selectedMonitor = ''

    if monitor == '1':
        selectedMonitor = get_monitorNumber()

    isLan = "lan" if isLanConfig(universalYesNo) == '1' else 'auto'

    isUsbMode = get_usbMode()

    if isUsbMode == '1':
        driveName, drivePath = get_driveUsbData()
    else:
        driveName, drivePath = get_driveData()

    if monitor == '1':
        command = f"xfreerdp /v:{ip} /u:{login} /p:{password} /t:{windowCaption} /network:{isLan} /rfx /gfx /compression /monitors:{selectedMonitor} /dynamic-resolution /clipboard /sound /drive:{driveName},{drivePath}"
    else:
        command = f"xfreerdp /v:{ip} /u:{login} /p:{password} /t:{windowCaption} /network:{isLan} /rfx /gfx /compression /multimon /dynamic-resolution /clipboard /sound /drive:{driveName},{drivePath}"

    runConnection(command, ip)

def runConnection(command, ip):
    print(f"\n\n    Nawiazuje polaczenie RDP z {ip}")
    try:
        print("    Polaczenie RDP zostalo pomyslnie nawiazane")
        subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("    Połączenie RDP zostalo pomyslnie zakonczone\n")
        print("    Dziekuje za skorzystanie ze skryptu\n")
    except subprocess.CalledProcessError as e:
        print("\n    Wystąpił nieoczekiwany blad. Sprawdz logi ponizej:\n")
        print(e.stderr.decode())
def handle_case(value):
    if value == '1':
        print("\n    Zakladka: Szybkie polaczenie\n")
        createFastConnection()
    elif value == '2':
        print("\n Zakladka: Polaczenie zaawansowane\n")
        createAdvancedConnection()
    else:
        print("\n Zakonczono dzialanie skryptu\n")
        exit()


handle_case(menuSelection)