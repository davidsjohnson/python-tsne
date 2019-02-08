import os
import json
import numpy as np
import scipy.io.arff
from sklearn import manifold

GENRES = "BLUES CLASSICAL COUNTRY DISCO HIPHOP JAZZ METAL POP REGGAE ROCK".split(" ")

# Class for Writing Data to JSON for DxR
class SongData(json.JSONEncoder):
    def __init__(self, features, label, fpath, x, y, z):
        self.name = fpath.split("/")[2].replace(".au", "")
        self.genre = GENRES[label]
        self.features = features.tolist()
        self.label = int(label)
        self.fpath = fpath
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

class TsneParams:
    def __init__(self, data_idx=0, n_components=3, p=30, lr=50, n_iter=1000, init="random"):
        self.data_idx = data_idx
        self.n_components = n_components
        self.p = p
        self.lr = lr
        self.n_iter = n_iter
        self.init = init

# global for easier modification via osc
tsne_params = TsneParams()

def load_from_arff(data_name, data_path):
    # Load features extracted using Marsyas
    data_name = "genres_mfcc"
    datafile = os.path.join(data_path, "{}.arff".format(data_name))
    data, _ = scipy.io.arff.loadarff(datafile)

    # load file names from arff file
    fs = []
    with open(datafile, 'r') as f:
        for line in f:
            if "filename" in line:
                fs.append(line.strip().split(" ")[2])

    # Convert data from numpy object list to numpy float array
    X = []
    Y = []
    label_idx = len(data[0])-1

    for row in data:
        X.append(list(row)[:label_idx])
        Y.append(int(list(row)[label_idx:][0]))

    return np.array(X), np.array(Y), np.array(fs)


def load_from_npz(data_name, data_path):
    fpath = os.path.join(data_path, "{}_data.npz".format(data_name))
    data = np.load(fpath)
    return data["X"], data["Y"], data["fs"]


def savez(data_name, data_path, X, Y, fs):
    fpath = os.path.join(data_path, "{}_data.npz".format(data_name))
    np.savez(fpath, X=X, Y=Y, fs=fs)


def run_tsne(X):
    tsne = manifold.TSNE(n_components=tsne_params.n_components, 
                         perplexity=tsne_params.p, 
                         learning_rate=tsne_params.lr, 
                         n_iter=tsne_params.n_iter, 
                         init=tsne_params.init,
                         random_state=1)
    return tsne.fit_transform(X)


def jsonify(X, Y, fs, Y_tsne):
    data_objs = []
    for (features, label, f, coords) in zip(X, Y, fs, Y_tsne):
        data_objs.append(SongData(features, label, f, *coords))

    return data_objs


def save_json(data_objs, filepath):
    with open(filepath, "w") as of:
        json.dump(data_objs, of, default=lambda x: x.__dict__, indent=4)


def update_json_specs(specfile, x_domain, y_domain, z_domain):
    with open(specfile, 'r') as f:
        data = json.load(f)

    data['encoding']['x']['scale']['domain'] = x_domain
    data['encoding']['y']['scale']['domain'] = y_domain
    data['encoding']['z']['scale']['domain'] = z_domain

    with open(specfile, 'w') as f:
        json.dump(data, f, indent=4)


def process(jsonpath, specspath):

    data_names = ["genres_default", "genres_mfcc"]
    data_path = "../data"

    print("Loading Data {} from ARFF File in {}...".format(data_names[tsne_params.data_idx], data_path))
    X, Y, fs = load_from_arff(data_names[tsne_params.data_idx], data_path)
    print("Done")
    print("Running TSNE | p: {} - lr: {} - iters: {} - init: {} - data: {}".format(tsne_params.p, tsne_params.lr, tsne_params.n_iter, tsne_params.init, data_names[tsne_params.data_idx]))
    Y_tsne = run_tsne(X)
    x_domain = [float(Y_tsne[:,0].min()), float(Y_tsne[:,0].max())]
    y_domain = [float(Y_tsne[:,1].min()), float(Y_tsne[:,1].max())]
    z_domain = [float(Y_tsne[:,2].min()), float(Y_tsne[:,2].max())]
    print("Done")
    print("Saving Data to JSON in Unity...")
    save_json(jsonify(X, Y, fs, Y_tsne), jsonpath)
    update_json_specs(specspath, x_domain, y_domain, z_domain)
    print("Done")

# receive data from pad pressed to trigger tnse
def osc_process_tsne(ogaddress, params, *args):
    process(params[0], params[1])
    print("Sending OSC...")
    params[2].send_message("/tsnepython/done", 0)  # send message requires some value...receiver can just ignore

def osc_update_param(ogaddress, param, *args):
    print("Updating Param: {} - {}".format(param[0], int(args[1])))
    tsne_params.__dict__[param[0]] = int(args[1])

def osc_update_init_param(ogaddress, param, *args):
    print("Updating Param: {} - {}".format(param[0], "random" if int(args[1]) == 0 else "pca"))
    tsne_params.__dict__[param[0]] = "random" if int(args[1]) == 0 else "pca" 

def run_osc(jsonpath, specspath):
    from pythonosc import dispatcher
    from pythonosc import osc_server

    from pythonosc import udp_client

    osc_client = udp_client.SimpleUDPClient("127.0.0.1", 10102)

    d = dispatcher.Dispatcher()
    d.map("/tsneprocess/pressed", osc_process_tsne, jsonpath, specspath, osc_client)
    d.map("/tsne_data/value", osc_update_param, "data_idx")
    d.map("/tsne_p/value", osc_update_param, "p")
    d.map("/tsne_lr/value", osc_update_param, "data_lr")
    d.map("/tsne_niters/value", osc_update_param, "n_iter")
    d.map("/tsne_init/value", osc_update_init_param, "init")


    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 10101), d)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--unity-tsne", default="../../unity/TSNE-3D2017")
    parser.add_argument("-o", "--osc", action="store_true")
    args = parser.parse_args()

    unity_tsnepath = args.unity_tsne
    tsne_datapath = "Assets/StreamingAssets/DxRData/song_data.json" 
    tsne_specspath = "Assets/StreamingAssets/DxRSpecs/tsne_scatterplot3D.json"
    jsonpath = os.path.join(unity_tsnepath, tsne_datapath)
    specspath = os.path.join(unity_tsnepath, tsne_specspath)

    if (args.osc):
        run_osc(jsonpath, specspath)
    else:
        process(jsonpath, specspath)

if __name__ == "__main__":
    main()
