from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

def print_osc(ogaddress, params, *args):
    string = ""
    for i in args:
        string = "{} {:.3}".format(string, i)
    print("OSC Message: {} - {}".format(ogaddress, string))

def run_osc():

    d = dispatcher.Dispatcher()
    d.map("/*", print_osc)

    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 40404), d)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


def main():
    run_osc()

if __name__ == '__main__':
    main()