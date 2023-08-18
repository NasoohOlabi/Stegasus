import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

file = 'stats2.tsv'


# Initialize dictionaries to store data for pie chart
share_data = {
    'fsb': [],
    'typo': [],
    'emo': []
}

df = pd.read_csv(f'Benchmarks/{file}', sep='\t')

def draw_cap(y_column,name):
	# Modify these column names based on your new TSV file
	x_column = 'cover size'

	df_sorted = df.sort_values(x_column)

	x = df_sorted[x_column]
	y = df_sorted[y_column]

	
	mean_bits = np.mean(df_sorted[y_column.replace('capacity','bits')])
	std_bits = np.std(df_sorted[y_column.replace('capacity','bits')])
	mean_x = np.mean(x)
	std_x = np.std(x)
	mean_y = np.mean(y)
	std_y = np.std(y)

	plt.title(name)
	plt.scatter(x, y, label='Samples')
	plt.grid(True)
	plt.xlabel(x_column)
	plt.ylabel('Capacity')

	plt.ylim(-2, 50)
	plt.legend()

	print(f'Mean Bits: {mean_bits:.2f}\nStd Bits: {std_bits:.2f}')
	print(f'Mean {x_column}: {mean_x:.2f}\nStd {x_column}: {std_x:.2f}')
	print(f'Mean Ratio: {mean_y:.2f}\nStd Ratio: {std_y:.2f}')

	plt.show()
	# plt.savefig(y_column)

import matplotlib.pyplot as plt

draw_cap('capacity','Stegasus')
print('#'*30)
draw_cap('typo capacity','Typoceros')
print('#'*30)
draw_cap('emo capacity','Emojier')
print('#'*30)
draw_cap('fsb capacity','Frustratingly Simple Bert')
print('#'*30)


# import numpy as np

# # Calculate average shares and store data for pie chart
# avg_share_fsb = np.mean(df['fsb share'])
# avg_share_typo = np.mean(df['typo share'])
# avg_share_emo = np.mean(df['emo share'])

# share_data['fsb'].append(avg_share_fsb)
# share_data['typo'].append(avg_share_typo)
# share_data['emo'].append(avg_share_emo)

# # Create the pie chart
# labels = [
#  'Frustratingly Simple Bert'
# , 'Typoceros'
# , 'Emojier'
# ]
# average_shares = [
# np.mean(share_data['fsb']),
# np.mean(share_data['typo']),
# np.mean(share_data['emo'])
# ]

# # Define cooler colors
# cool_colors = ['#66c2a5', '#fc8d62', '#8da0cb']

# plt.title('Average Share Distribution')
# plt.pie(average_shares, labels=labels, autopct='%1.1f%%', startangle=140, colors=cool_colors)
# plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

# # Add legend outside the pie chart
# plt.legend(labels, title="Layers", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# plt.tight_layout()  # Adjust layout to prevent labels from being cut off

# # plt.show()
# plt.savefig('pie.png', dpi=300, bbox_inches='tight')  # Save the figure with higher resolution
