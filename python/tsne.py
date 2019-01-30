import os
import json
import numpy as np
import scipy.io.arff
from sklearn import manifold

from pythonosc import dispatcher
from pythonosc import osc_server

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


def run_tsne(X, n_components=3, p=30, lr=50, n_iter=500, init="random"):
    tsne = manifold.TSNE(n_components=n_components, perplexity=p, learning_rate=lr, n_iter=n_iter, init=init)
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


def process(jsonpath, specspath, data_idx=0, n_components=3, p=30, lr=50, n_iter=1000, init="random"):

    data_names = ["genres_default", "genres_mfcc"]
    data_path = "../data"

    print("Loading Data {} from ARFF File in {}...".format(data_names[data_idx], data_path))
    X, Y, fs = load_from_arff(data_names[data_idx], data_path)
    print("Done")
    print("Running TSNE...")
    Y_tsne = run_tsne(X, n_components=n_components, p=p, lr=lr, n_iter=n_iter, init=init)
    x_domain = [float(Y_tsne[:,0].min()), float(Y_tsne[:,0].max())]
    y_domain = [float(Y_tsne[:,1].min()), float(Y_tsne[:,1].max())]
    z_domain = [float(Y_tsne[:,2].min()), float(Y_tsne[:,2].max())]
    print("Done")
    print("Saving Data to JSON in Unity...")
    save_json(jsonify(X, Y, fs, Y_tsne), jsonpath)
    update_json_specs(specspath, x_domain, y_domain, z_domain)
    print("Done")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--unity-tsne", default="../../unity/TSNE-3D2017")

    args = parser.parse_args()
    unity_tsnepath = args.unity_tsne
    tsne_datapath = "Assets/StreamingAssets/DxRData/song_data.json" 
    tsne_specspath = "Assets/StreamingAssets/DxRSpecs/tsne_scatterplot3D.json"
    jsonpath = os.path.join(unity_tsnepath, tsne_datapath)
    specspath = os.path.join(unity_tsnepath, tsne_specspath)

    process(jsonpath, specspath)

if __name__ == "__main__":
    main()