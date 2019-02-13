from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from scipy.spatial import distance

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
    with open(logfile, 'r') as logf:
        for line in logf:
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

def read_oscxr_pad_log(logfile):
    log_data = []
    log_ts = []
    with open(logfile, 'r') as logf:
        for line in logf:
            line = line[:-2].split(" - ")       # parse data

            if line[3] == "pad":        # only include pad data from log
                # convert timestamp to milliseconds
                ms = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S,%f').timestamp() * 1000 # parse time to milliseconds
                log_ts.append(ms)
                
                # get osc value
                log_data.append(1)  # ignoring velocity and only appending 1

    #normalize ts to first entry being zero ms
    log_ts = np.array(log_ts)
    log_ts = log_ts - log_ts.min()

    return np.array(log_data), log_ts
    

def calc_pad_error(actual, expected):
    return np.average(np.abs(actual - expected))

def calc_slider_error(actual, actual_ts, expected, exp_ts):
    exp_temp = []
    bar_start_idx = 0
    for ts in actual_ts:
        if bar_start_idx + 1 < len(exp_ts):
            if ts >= exp_ts[bar_start_idx+1]:
                bar_start_idx += 1

        exp_temp.append(expected[bar_start_idx])

    return np.linalg.norm(actual-exp_temp)


def plot_logfiles():
    tos_file = "logs/touchosc_slider_{}.log"
    top_file = "logs/touchosc_pad_{}.log"

    oxs_file = "logs/oscxr_slider_{}.log"
    oxp_file = "logs/oscxr_pad_{}.log"

    num_runs = 10

    ## Slider Data
    exp_s_data, exp_s_ts = generate_expected_slider()

    # Process OSC-XR Slider Data
    errors_slider = []
    for i in range(num_runs):
        oxs_data, oxs_ts = read_log_file(oxs_file.format(i))
        plt.plot(oxs_ts, oxs_data[:,1], c="orange")             # need to account for ID in osx_data 
        errors_slider.append(calc_slider_error(oxs_data[:,1], oxs_ts, exp_s_data, exp_s_ts))

    print("Average Slider Error (dist) OSC-XR: {}".format(np.average(errors_slider)))

    plt.plot(exp_s_ts, exp_s_data, label="expected", linewidth=2)
    plt.title("OSC-XR Fader Performance")
    plt.ylabel("Fader Value")
    plt.xlabel("Time (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("oscxr_slider_eval.pdf")
    plt.show()
    
    # Process TouchOSC Slider Data
    errors_slider = []
    for i in range(num_runs):
        tos_data, tos_ts = read_log_file(tos_file.format(i))
        tos_data = tos_data.squeeze()
        plt.plot(tos_ts, tos_data, c='orange')
        errors_slider.append(calc_slider_error(tos_data, tos_ts, exp_s_data, exp_s_ts))

    print("Average Slider Error (dist) TouchOSC: {}".format(np.average(errors_slider)))

    plt.plot(exp_s_ts, exp_s_data, label="expected", linewidth=2)
    plt.title("TouchOSC Fader Performance")
    plt.ylabel("Fader Value")
    plt.xlabel("Time (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("touchosc_slider_eval.pdf")
    plt.show()


    ## Process Pad Data
    exp_p_data, exp_p_ts = generate_expected_pad()

    # OSC-XR Pad Data
    errors_pad = []
    for i in range(num_runs):
        oxp_data, oxp_ts = read_oscxr_pad_log(oxp_file.format(i))

        # get rid pad releases (touchosc) and first entry
        oxp_data = oxp_data.squeeze()
        oxp_ts = oxp_ts[oxp_data==1][1:]
        oxp_data = oxp_data[oxp_data==1][1:]
        # renormalize time to first entry
        oxp_ts = oxp_ts - oxp_ts.min()

        oxp_data = oxp_data + (i / 100.0) + .01
        plt.scatter(oxp_ts, oxp_data)

        errors_pad.append(calc_pad_error(oxp_ts, exp_p_ts))

    print("Average Pad Error (ms) OSC-XR: {}".format(np.average(errors_pad)))

    plt.scatter(exp_p_ts, exp_p_data, c='g', marker="s", label='expected')
    plt.ylim((.87,1.23))
    plt.xlim((-300, 4990))
    plt.title("OSC-XR Button Performance")
    plt.yticks([])
    plt.ylabel("Test Iteration")
    plt.xlabel("Time (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("oscxr_pad_eval.pdf")
    plt.show()

    # TouchOSC Pad Data
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
    plt.tight_layout()
    plt.savefig("touchosc_pad_eval.pdf")
    plt.show()

   


if __name__ == "__main__":
    plot_logfiles()