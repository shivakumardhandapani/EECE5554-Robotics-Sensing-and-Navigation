#Collaborated with Palaniappan Yeagappan, Sai Sreekar K S, Yogeshwaran Eswaran
#!/usr/bin/env python3
import rosbag
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

def read_rosbag(bag_file, topic='/gps'):
    bag = rosbag.Bag(bag_file)
    data = {'easting': [], 'northing': [], 'altitude': [], 'time': []}

    for topic, msg, t in bag.read_messages(topics=[topic]):
        data['easting'].append(msg.utm_easting)
        data['northing'].append(msg.utm_northing)
        data['altitude'].append(msg.altitude)
        data['time'].append(msg.header.stamp.to_sec())

    bag.close()

    # Convert lists to numpy arrays
    for key in data:
        data[key] = np.array(data[key])

    return data

def compute_centroid(data):
    centroid = np.mean(data, axis=0)
    return centroid

def compute_offset(centroid_unocc, centroid_occ):
    offset = centroid_occ - centroid_unocc
    print("Total Offset (Easting, Northing):", offset)
    return offset

def compute_deviation(data, centroid):
    deviation = data - centroid
    return deviation

def plot_histogram(ax, data, bins, color, alpha, label, xlabel, ylabel, title):
    ax.hist(data, bins=bins, color=color, alpha=alpha, label=label)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

def plot_line(x, y, color, linestyle, label):
    slope, intercept, _, _, _ = linregress(x, y)
    x_fit = np.linspace(min(x), max(x), 100)
    y_fit = slope * x_fit + intercept
    plt.plot(x_fit, y_fit, color=color, linestyle=linestyle, label=label)

#Bag files for standalone GPS data:
#bag_file_open = '/home/shivakumardhandapani/gnss/data/open.bag'
#bag_file_occluded = '/home/shivakumardhandapani/gnss/data/occluded.bag'
#bag_file_walking = '/home/shivakumardhandapani/gnss/data/walking.bag'

#Bag files for RTK GPS data:
bag_file_open = '/home/shivakumardhandapani/gnss/data/openRTK.bag'
bag_file_occluded = '/home/shivakumardhandapani/gnss/data/occludedRTK.bag'
bag_file_walking = '/home/shivakumardhandapani/gnss/data/walkingRTK.bag'

# Process Occluded bag file
data_occluded = read_rosbag(bag_file_occluded)

# Process Open bag file
data_open = read_rosbag(bag_file_open)

# Process Walking bag file
data_walking = read_rosbag(bag_file_walking)

# Calculate centroids and offsets
centroid_open = compute_centroid(np.column_stack((data_open['easting'], data_open['northing'])))
centroid_occluded = compute_centroid(np.column_stack((data_occluded['easting'], data_occluded['northing'])))
offset = compute_offset(centroid_open, centroid_occluded)

# Calculate deviations from centroids
deviation_open = compute_deviation(np.column_stack((data_open['easting'], data_open['northing'])), centroid_open)
deviation_occluded = compute_deviation(np.column_stack((data_occluded['easting'], data_occluded['northing'])), centroid_occluded)
deviation_walking = compute_deviation(np.column_stack((data_walking['easting'], data_walking['northing'])), centroid_occluded)

# Plotting

# Stationary northing vs. easting scatterplot
plt.figure(figsize=(8, 6))
plt.scatter(deviation_open[:, 0], deviation_open[:, 1], color='pink', label='Open', marker='x')
plt.scatter(deviation_occluded[:, 0], deviation_occluded[:, 1], color='purple', label='Occluded', marker='*')
plt.xlabel("Deviation in Easting (m)")
plt.ylabel("Deviation in Northing (m)")
plt.title("Stationary Northing vs. Easting Scatterplot")
plt.text(centroid_open[0], centroid_open[1], f"Total Offset: {offset}", fontsize=12, color='green', ha='center')
plt.grid(True)
plt.legend()
plt.show()

# Stationary altitude vs. time plot
plt.figure(figsize=(8, 6))
plt.plot(data_open['time'], data_open['altitude'], color='pink', label='Open', marker='x')
plt.plot(data_occluded['time'], data_occluded['altitude'], color='purple', label='Occluded', marker='*')
plt.title("Stationary Altitude")
plt.xlabel("Time (sec)")
plt.ylabel("Altitude (m)")
plt.grid(True)
plt.legend()
plt.show()

# Stationary histogram plots for position from the centroid
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

plot_histogram(axes[0], deviation_open[:, 0], bins=30, color='pink', alpha=0.5, label='Open',
               xlabel='Deviation in Easting (m)', ylabel='Frequency', title='Stationary Easting Histogram (Open)')

plot_histogram(axes[1], deviation_occluded[:, 0], bins=30, color='purple', alpha=0.5, label='Occluded',
               xlabel='Deviation in Easting (m)', ylabel='Frequency', title='Stationary Easting Histogram (Occluded)')

plt.tight_layout()
plt.show()

# Euclidean distance histograms
euclidean_distance_open = np.sqrt(deviation_open[:, 0]**2 + deviation_open[:, 1]**2)
euclidean_distance_occluded = np.sqrt(deviation_occluded[:, 0]**2 + deviation_occluded[:, 1]**2)

plt.figure(figsize=(8, 6))
plot_histogram(plt.gca(), euclidean_distance_open, bins=30, color='pink', alpha=0.5, label='Open',
               xlabel='Euclidean Distance', ylabel='Frequency', title='Euclidean Distance Histogram')

plot_histogram(plt.gca(), euclidean_distance_occluded, bins=30, color='purple', alpha=0.5, label='Occluded',
               xlabel='Euclidean Distance', ylabel='Frequency', title='Euclidean Distance Histogram')

plt.grid(True)
plt.show()

# Moving (walking) data northing vs. easting scatterplot with line of best fit
plt.figure(figsize=(8, 6))
plt.scatter(data_walking['easting'], data_walking['northing'], color='brown', label='Walking', marker='o')
plot_line(data_walking['easting'], data_walking['northing'], 'grey', '--', 'Line of Best Fit')
plt.xlabel("Easting (m)")
plt.ylabel("Northing (m)")
plt.title("Moving (Walking) Data Scatterplot")
plt.grid(True)
plt.legend()
plt.show()

# Moving (walking) data altitude vs. time plot
plt.figure(figsize=(8, 6))
plt.plot(data_walking['time'], data_walking['altitude'], color='grey', label='Walking Data', marker='o')
plt.title("Moving (Walking) Data Altitude")
plt.xlabel("Time (sec)")
plt.ylabel("Altitude (m)")
plt.grid(True)
plt.show()

# Calculate RMSE for stationary datasets
rmse_open = np.sqrt(np.mean((deviation_open[:, 0])**2 + (deviation_open[:, 1])**2))
rmse_occluded = np.sqrt(np.mean((deviation_occluded[:, 0])**2 + (deviation_occluded[:, 1])**2))

print("RMSE for Open stationary dataset:", rmse_open)
print("RMSE for Occluded stationary dataset:", rmse_occluded)

# Fit a line to the walking data
slope, intercept, _, _, _ = linregress(data_walking['easting'], data_walking['northing'])

# Compute predicted y-values
y_fit = slope * data_walking['easting'] + intercept

# Compute residuals
residuals = data_walking['northing'] - y_fit

# Compute RMSE of residuals
rmse_walk_line = np.sqrt(np.mean(residuals**2))

print("RMSE from Line of Best Fit to Walking Data:", rmse_walk_line)
