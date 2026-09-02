import os
import subprocess

def vulnerable_ping():
    # Επικίνδυνη πρακτική: Απευθείας εκτέλεση user input στο OS shell
    user_input = input("Enter IP: ")
    
    # 1. Command Injection μέσω os.system
    os.system("ping -c 1 " + user_input)
    
    # 2. Command Injection μέσω subprocess με shell=True
    subprocess.run(f"ping -c 1 {user_input}", shell=True)

if __name__ == "__main__":
    vulnerable_ping()
