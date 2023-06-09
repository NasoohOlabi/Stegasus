import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

df = pd.read_csv('MLM benchmark.tsv', sep='\t')
df_sorted = df.sort_values('cover size')  # Sort the data based on 'cover size'


import matplotlib.pyplot as plt
import numpy as np

# Assuming you have three columns in your DataFrame named "bits", "cover size", and "ratio"
x = df_sorted['cover size']
y = df_sorted['ratio']

# Fit a logarithmic curve using the method of least squares
coefficients = np.polyfit(np.log(x), y, 1)

# Generate new x-values for plotting
x_new = np.linspace(min(x), max(x), 100)

# Evaluate the logarithmic curve using the new x-values
y_new = np.polyval(coefficients, np.log(x_new))

# Calculate mean and standard deviation of "bits", "cover size", and "ratio" columns
mean_bits = np.mean(df_sorted['bits'])
std_bits = np.std(df_sorted['bits'])
mean_cover_size = np.mean(df_sorted['cover size'])
std_cover_size = np.std(df_sorted['cover size'])
mean_ratio = np.mean(df_sorted['ratio'])
std_ratio = np.std(df_sorted['ratio'])

# Plot the original data and the fitted curve
plt.scatter(x, y, label='Original Data')
plt.plot(x_new, y_new, color='red', label='Fitted Logarithmic Curve')
plt.grid(True)
plt.xlabel('Cover Size')
plt.ylabel('Ratio')
plt.legend()

# Add text annotations for mean and standard deviation
print(f'Mean Bits: {mean_bits:.2f}\nStd Bits: {std_bits:.2f}')
print(f'Mean Cover Size: {mean_cover_size:.2f}\nStd Cover Size: {std_cover_size:.2f}')
print(f'Mean Ratio: {mean_ratio:.2f}\nStd Ratio: {std_ratio:.2f}')

# Show the plot
plt.show()
