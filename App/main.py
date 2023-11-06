import os
import logging

from Commands import ScrapingHandler
from Commands.consoleColors import bcolors as ccolors
from Commands.InsertDataExcel import InsertExcel
from Commands.ManageData import ManageData

mainPath = os.path.dirname(os.path.abspath(__file__))

log_file = "appError.log"
logging.basicConfig(filename=log_file, level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')  

def main():
    while True:
        try:
            print("--"*40)
            print(f"Automated Tasks")
            print(f"1-) Scrape whole website, convert to data, insert to excel.")
            print(f"2-) Scrape new products, convert to data, insert to excel.")
            print("--"*40)
            print(f"Manuel Tasks")
            print(f"3-) Scrape whole website")
            print(f"4-) Scrape new products")
            print(f"5-) Convert scrape datas to product data")
            print(f"6-) Insert product datas to excel.\n")
            
            choice = int(input(f"Choose: "))
            
            if choice == 2:
                print(f"The process has just started. Waiting for GUI...")
                ScrapingHandler(2, mainPath)
            else:
                clearConsole()
                print("Just second option is avaible!")
                
        except ValueError:
            clearConsole()
            print("You have not entered right input type.")
        except Exception as e:
            clearConsole()
            print("Some errors have occurred.")
            print(f"The error logged on {mainPath}\\appError.log")
            logging.error(str(e) + "\n-----ERROR END-----\n", exc_info=True)
    
main()