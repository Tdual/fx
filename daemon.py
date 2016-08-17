import sys
import os
import trade

def fork():
    pid = os.fork()
    if pid > 0:
        with open('/var/run/gpio_fan_controld.pid','w') as f:
            f.write(str(pid)+"\n")
        sys.exit()

    if pid == 0:
        trade.main(10*60)

if __name__=='__main__':
    fork()
