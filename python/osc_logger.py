import sys
import logging

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

logger = logging.getLogger('osc')   # Cheating...

def log_osc(ogaddress, params, *args):
    string = ""
    for i in args:
        string = "{} {:.4},".format(string, i)
    logger.info("{} - {} - {} - {}".format(params[0], params[1], ogaddress, string))


def run_osc(logfile):

    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format = FORMAT, filename=logfile, filemode='w', level=logging.DEBUG)

    d = dispatcher.Dispatcher()
    # OSC XR Addresses
    d.map("/slider/value", log_osc, "slider", "oscxr")
    d.map("/gyro/values", log_osc, "gyro", "oscxr")
    d.map("/pad/pressed", log_osc, "pad", "oscxr")

    # Touch OSC Addresses
    d.map("/1/freq", log_osc, "slider", "touchosc")
    d.map("/1/push", log_osc, "pad", "touchosc")
    d.map("/accxyz", log_osc, "acc", "touchosc")

    server = osc_server.ThreadingOSCUDPServer(("192.168.0.14", 40404), d)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


def main(logfile):
    run_osc(logfile)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No file name given")
        sys.exit(-1)

    main(sys.argv[1])