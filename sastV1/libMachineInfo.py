#!/usr/bin/python3
#
# Raspberry Pi 本体の情報を取得 python3版
import logging
import os
import subprocess
import time
import sys
import psutil
import signal

SAST_MONITOR = "SAST_monitor.py"
def sendSIG4Monitor():
    logging.debug("[sendSIG4Monitor]")
    pid = None
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if(proc.info["name"] == SAST_MONITOR):
            pid = proc.info["pid"]
    if( pid == None ):
        return False
    logging.debug(f"Monitor PID {pid}")
    os.kill(int(pid), signal.SIGUSR1)
    return True

def getHostname():
    return f"{os.uname()[1]}"

def getIPAddr():
    cmd = "ip a show wlan0 | grep 'inet ' | cut -f6 -d ' ' | cut -d '/' -f1"
    IP = subprocess.check_output(cmd, shell = True ).decode()
    if( IP != None ):
        IP = IP.strip()
    return IP

def getIPAddrV6():
    cmd = "ip a show wlan0 | grep 'inet6 ' | cut -f6 -d ' ' | cut -d '/' -f1" 
    IP = subprocess.check_output(cmd, shell = True ).decode()
    IPv6 = IP.split('\n')[0]
    return IPv6

def getTypeIP(IP):
    if( IP.startswith('169.254') ):
        return False
    elif( IP.startswith('0.0.0.0')):
        return False
    elif( IP.startswith('192.168')):
        return True
    elif( IP.startswith('172.16')):
        return True
    elif( IP.startswith('10.')):
        return True
    else:
        return False

def resetDHCP():
    subprocess.check_output(['/sbin/dhclient','-r'], shell=True)
    time.sleep(5)
    subprocess.check_output(['/sbin/dhclient'], shell=True)
    time.sleep(1)
    print("IP = {getIPAddr()}")

def getDefaultRoute():
    cmd = "/sbin/route | /bin/grep default | /usr/bin/awk '{print $2}'"
    routeIP = subprocess.check_output(cmd, shell = True ).decode()
    if( routeIP == "0.0.0.0" ):
        return None
    return routeIP.strip()

def IsAlive(IPAddr):
    cmd = f"/bin/ping -c 3 {IPAddr} "
    ret = subprocess.run(['/bin/ping','-c','2',IPAddr],stdout=subprocess.DEVNULL)
    #ret = subprocess.run(f"[{cmd):")
    #print(ret)
    if( ret.returncode == 0 ):
        return True
    return False

def getSSID():
    try:
        cmd = "/sbin/iwgetid -r"
        SSID = subprocess.check_output(cmd, shell = True ).decode()
        return SSID
    except Exception as e:
        logging.warinig("Exeption:{0}".format(e))
        return None

def getMachine_Temp():
    temp =  subprocess.run("vcgencmd measure_temp", shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
    temp = temp[1].split("'")
    logging.debug("Machine Temp:{}C".format(temp[0]))
    return float(temp[0])

def getMachine_Clock():
    freq = subprocess.run("vcgencmd measure_clock arm", shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
    freq = int(freq[1].replace('\n', '')) / 1000000000
    logging.debug("Machine Clock:{}GHz".format(freq))
    return freq

def getMachine_Volt():
    volt = subprocess.run("vcgencmd measure_volts", shell=True, encoding='utf-8', stdout=subprocess.PIPE).stdout.split('=')
    volt = volt[1].replace('\n', '')
    volt = float(volt.replace('V',''))
    logging.debug("Machine Volt:{}V".format(volt))
    return volt

def getSerial():
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        cpuserial = line[10:26]
    f.close()
  except:
    cpuserial = None
  return cpuserial

if __name__ == '__main__':
    MyIP = getIPAddr()
    MyIPv6 = getIPAddrV6()
    print(f"MyIP is {MyIP}({MyIPv6})") 
    if( getTypeIP(MyIP) == False ):
        print(f" in auto Private or Externa")

    IP = getDefaultRoute()
    ret = IsAlive(IP)
    print(f"default router {IP} is {ret}")

    IP = "www.google.com"
    print(f"{IP} is {ret}")
    
    print(f"Machine Serial : {getSerial()}")


    sys.exit(0)

    try:
        while True :
            print("{}({}) : {} / {} / {}".format( 
                getHostname(), getIPAddr(), getMachine_Temp(), 
                getMachine_Clock(), getMachine_Volt())
                )
            time.sleep(1)
    except KeyboardInterrupt:
        import sys
        sys.exit()

        
