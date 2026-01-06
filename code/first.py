import spectral
import numpy as np
import matplotlib.pyplot as plt

# Load ENVI file
img = spectral.open_image("data\I99.bil.hdr")
cube = img.load()   # shape: (rows, cols, bands)

# print("Shape:", cube.shape)
# print("Data type:", cube[21,24, :].dtype)
# print("Data :", cube[14,20])

# Pixel coordinates
y1, x1 = 50, 120   # Pixel A
y2, x2 = 75, 123  # Pixel B

spectrum_A = cube[y1, x1, :]
spectrum_A_squeezed = np.squeeze(spectrum_A)
spectrum_B = cube[y2, x2, :]
spectrum_B_squeezed= np.squeeze(spectrum_B)
print(f"Spectrum at Pixel A ({x1},{y1}):", spectrum_A)


plt.figure()
plt.plot(spectrum_A_squeezed, label=f"Pixel A ({x1},{y1})")
plt.plot(spectrum_B_squeezed, label=f"Pixel B ({x2},{y2})")
plt.xlabel("Band index")
plt.ylabel("Intensity / Reflectance")
plt.title("Spectral Comparison of Two Pixels")
plt.legend()
plt.show()

# y, x = 150, 150   # center pixel
# window = 5
# half = window // 2

# region = cube[
#     y-half:y+half+1,
#     x-half:x+half+1,
#     :
# ]

# mean_spectrum = region.mean(axis=(0, 1))
# band_min = cube.min(axis=(0, 1))
# band_max = cube.max(axis=(0, 1))

# plt.figure()
# plt.plot(band_min, label="Min")
# plt.plot(band_max, label="Max")
# plt.plot(mean_spectrum , label="Mean", linestyle='--')
# plt.xlabel("Band index")
# plt.ylabel("Value")
# plt.title("Band-wise Min / Max")
# plt.legend()
# plt.show()












# import numpy as np

# Create a sample 3D array (height=10, width=10, channels=3)
# cube = np.arange(300).reshape((10, 10, 3))

# print(cube)
# print(cube[0])

# Define example parameters
# y = 5
# x = 5
# half = 2

# # # Apply the slicing
# region = cube[y-half:y+half+1, x-half:x+half+1, :]

# print(f"Original cube shape: {cube.shape}")
# # print(f"Slice parameters: y={y}, x={x}, half={half}")
# # print(f"Calculated y slice: {y-half}:{y+half+1}") # 3:8
# # print(f"Calculated x slice: {x-half}:{x+half+1}") # 3:8
# print(f"Resulting region shape: {region.shape}")
