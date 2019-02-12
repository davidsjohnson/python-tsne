from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

def generate_expected_slider(bpm = 90):

    mspb = (1/bpm)*60000
    vals = [.25, .75, .50, 1.0]
    exp_data = []
    exp_ts = []
    for i, v in enumerate(vals):
        exp_data.extend([v]*2)
        exp_ts.extend([mspb*(i*4), mspb*(i*4) + mspb*4])
    exp_data.append(0)
    exp_ts.append(mspb*((i+1)*4))

    return np.array(exp_data), np.array(exp_ts)

def generate_expected_pad(bpm = 90, num_beats = 8):

    mspb = (1/bpm)*60000
    exp_data = []
    exp_ts = []
    for i in range(num_beats):
        exp_data.append(1)
        exp_ts.append(mspb * i)

    return np.array(exp_data), np.array(exp_ts)

# read files
def read_log_file(logfile):

    log_data = []
    log_ts = []
    with open(logfile, 'r') as tosf:
        for line in tosf:
            line = line[:-2].split(" - ")       # parse data

            # convert timestamp to milliseconds
            ms = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S,%f').timestamp() * 1000 # parse time to milliseconds
            log_ts.append(ms)
            
            # get osc values
            vals = []
            for val in line[-1].split(","):
                vals.append(float(val))
            log_data.append(vals)

    #normalize ts to first entry being zero ms
    log_ts = np.array(log_ts)
    log_ts = log_ts - log_ts.min()

    return np.array(log_data), log_ts

def calc_pad_error(actual, expected):
    return np.average(np.abs(actual - expected))

def calc_slider_error(actual, expected):
    return np.linalg.norm(actual-expected)


def plot_logfiles():
    tos_file = "logs/touchosc_slider_{}.log"
    top_file = "logs/touchosc_pad_{}.log"

    num_runs = 10

    # Process Slider Data
    exp_s_data, exp_s_ts = generate_expected_slider()
    errors_slider = []
    for i in range(num_runs):
        tos_data, tos_ts = read_log_file(tos_file.format(i))
        plt.plot(tos_ts, tos_data, c='orange')
        errors_slider.append(calc_slider_error(tos_data, exp_s_data))

    print("Average Slider Error (dist) TouchOSC: {}".format(np.average(errors_slider)))

    plt.plot(exp_s_ts, exp_s_data, label="expected", linewidth=2)
    plt.title("TouchOSC Fader Performance")
    plt.ylabel("Fader Value")
    plt.xlabel("Time (ms)")
    plt.legend()
    plt.savefig("touchosc_slider_eval.pdf")
    plt.show()

    # ## Process Pad Data
    exp_p_data, exp_p_ts = generate_expected_pad()
    errors_pad = []
    for i in range(num_runs):
        top_data, top_ts = read_log_file(top_file.format(i))

        # get rid pad releases (touchosc) and first entry
        top_data = top_data.squeeze()
        top_ts = top_ts[top_data==1][1:]
        top_data = top_data[top_data==1][1:]
        # renormalize time to first entry
        top_ts = top_ts - top_ts.min()

        top_data = top_data + (i / 100.0) + .01
        plt.scatter(top_ts, top_data)

        errors_pad.append(calc_pad_error(top_ts, exp_p_ts))

    print("Average Pad Error (ms) TouchOSC: {}".format(np.average(errors_pad)))

    plt.scatter(exp_p_ts, exp_p_data, c='g', marker="s", label='expected')
    plt.ylim((.87,1.23))
    plt.xlim((-300, 4990))
    plt.title("TouchOSC Button Performance")
    plt.yticks([])
    plt.ylabel("Test Iteration")
    plt.xlabel("Time (ms)")
    plt.legend()
    plt.savefig("touchosc_pad_eval.pdf")
    plt.show()

   


if __name__ == "__main__":
    plot_logfiles()