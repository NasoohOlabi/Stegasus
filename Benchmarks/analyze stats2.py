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

	coefficients = np.polyfit(np.log(x), y, 1)
	x_new = np.linspace(min(x), max(x), 100) # type: ignore
	y_new = np.polyval(coefficients, np.log(x_new))

	mean_bits = np.mean(df_sorted['bits'])
	std_bits = np.std(df_sorted['bits'])
	mean_x = np.mean(x)
	std_x = np.std(x)
	mean_y = np.mean(y)
	std_y = np.std(y)

	plt.title(name)
	plt.scatter(x, y, label='Samples')
	plt.plot(x_new, y_new, color='red', label='Tendency')
	plt.grid(True)
	plt.xlabel(x_column)
	plt.ylabel('Capacity')

	plt.ylim(-2, 50)
	plt.legend()

	print(f'Mean Bits: {mean_bits:.2f}\nStd Bits: {std_bits:.2f}')
	print(f'Mean {x_column}: {mean_x:.2f}\nStd {x_column}: {std_x:.2f}')
	print(f'Mean Ratio: {mean_y:.2f}\nStd Ratio: {std_y:.2f}')

	plt.show()
	plt.savefig(y_column)

draw_cap('capacity','Stegasus')
draw_cap('typo capacity','Typoceros')
draw_cap('emo capacity','Emojier')
draw_cap('fsb capacity','Frustratingly Simple Bert')

# Calculate average shares and store data for pie chart
avg_share_fsb = np.mean(df['fsb share'])
avg_share_typo = np.mean(df['typo share'])
avg_share_emo = np.mean(df['emo share'])

share_data['fsb'].append(avg_share_fsb)
share_data['typo'].append(avg_share_typo)
share_data['emo'].append(avg_share_emo)

# Create the pie chart
labels = ['fsb', 'typo', 'emo']
average_shares = [
np.mean(share_data['fsb']),
np.mean(share_data['typo']),
np.mean(share_data['emo'])
]

plt.title('Average Share Distribution')
plt.pie(average_shares, labels=labels, autopct='%1.1f%%', startangle=140)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

plt.show()
plt.savefig('pie')