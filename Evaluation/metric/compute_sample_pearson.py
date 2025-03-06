import pandas as pd
import ast
from scipy.stats import pearsonr

judgement_file_path = '*****.xlsx'
df = pd.read_excel(judgement_file_path, dtype=str)


def str_to_dict(s):
    return ast.literal_eval(s) if pd.notnull(s) else {}


df['rating'] = df['rating'].apply(str_to_dict)
df['human_rating'] = df['human_rating'].apply(str_to_dict)


def calculate_pearson(row):
    rating_dict = row['rating']
    human_rating_dict = row['human_rating']

    common_keys = set(rating_dict.keys()) & set(human_rating_dict.keys())

    rating_values = []
    human_rating_values = []

    for key in common_keys:
        if isinstance(rating_dict[key], list) and isinstance(human_rating_dict[key], list):
            rating_values.append(rating_dict[key][0])
            human_rating_values.append(human_rating_dict[key][0])

    if len(set(rating_values)) > 1 and len(set(human_rating_values)) > 1:
        if len(rating_values) > 1:
            pearson_corr, _ = pearsonr(rating_values, human_rating_values)
        else:
            pearson_corr = float('nan')
    else:
        pearson_corr = float('nan')

    return pearson_corr


grouped_pearson_dict = {}

try:
    for cat, group in df.groupby('category'):
        # Calculate Pearson for each sample in the group
        group['sample_pearson'] = group.apply(calculate_pearson, axis=1)
        group_average_pearson = group['sample_pearson'].mean()  # Average Pearson for the group
        grouped_pearson_dict[cat] = group_average_pearson
        print(f"The average Pearson correlation coefficient for category '{cat}' is: {group_average_pearson:.4f}")
except Exception as e:
    print(f"An error occurred during group processing: {e}")

# Calculate the overall average Pearson correlation across all samples
df['sample_pearson'] = df.apply(calculate_pearson, axis=1)
overall_average_pearson = df['sample_pearson'].mean()

# Save the results to a new Excel file
df.to_excel('sample_pearson_scores.xlsx', index=False)

# Print the overall Pearson correlation coefficient
print(f"Overall average Pearson correlation coefficient: {overall_average_pearson:.4f}")
