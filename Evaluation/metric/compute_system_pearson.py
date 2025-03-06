import pandas as pd
from scipy.stats import pearsonr


def load_data(file_path):
    data = pd.read_excel(file_path)
    return data


def calculate_category_pearson(data):
    correlation_dict = {}
    try:
        for cat, group in data.groupby('category'):
            group_score = group['score'].dropna()  # Drop missing values
            group_human_score = group['human_scores'].dropna()  # Drop missing values

            # Ensure both groups have the same length after dropping NaNs
            if len(group_score) == len(group_human_score):
                correlation, _ = pearsonr(group_score, group_human_score)
                correlation_dict[cat] = correlation
                print(f"The Pearson correlation coefficient for category '{cat}' is: {correlation:.4f}")
            else:
                print(f"Warning: Mismatched data lengths for category '{cat}', skipping correlation calculation.")
    except Exception as e:
        print(f"An error occurred during category processing: {e}")
        # Show value counts for categories in case of error
        category_counts = data['category'].value_counts()
        print(f"Category counts:\n{category_counts}")

    return correlation_dict


def calculate_overall_pearson(data):
    score = data['score'].dropna()
    human_score = data['human_scores'].dropna()

    if len(score) == len(human_score):
        total_correlation, _ = pearsonr(score, human_score)
        print(f"The overall Pearson correlation coefficient between score and human score is: {total_correlation:.4f}")
        return total_correlation
    else:
        print("Warning: Mismatched overall data lengths, unable to compute the overall Pearson correlation.")
        return None


def main():
    # your judgement excel file
    file_path = '*****.xlsx'

    data = load_data(file_path)

    required_columns = ['category', 'score', 'human_scores']
    if not all(col in data.columns for col in required_columns):
        raise ValueError(f"The dataset must contain the following columns: {', '.join(required_columns)}")

    print('Data successfully loaded')

    # Calculate Pearson correlations by category
    correlation_dict = calculate_category_pearson(data)

    # Calculate the overall Pearson correlation
    calculate_overall_pearson(data)

    correlation_results = pd.DataFrame(list(correlation_dict.items()), columns=['category', 'pearson_correlation'])
    correlation_results.to_excel('category_pearson_correlation_results.xlsx', index=False)


if __name__ == "__main__":
    main()
