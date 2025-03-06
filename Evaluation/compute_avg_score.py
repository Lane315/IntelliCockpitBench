import json
import os
import argparse


def process_jsonl(file_path):
    categories = {}
    total_score = 0
    total_count = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    category = data.get("category")
                    score = data.get("score")

                    if category is None or score is None:
                        print(f"Skipping line due to missing 'category' or 'score': {line.strip()}")
                        continue

                    if category not in categories:
                        categories[category] = {"total_score": 0, "count": 0}

                    categories[category]["total_score"] += score
                    categories[category]["count"] += 1

                    total_score += score
                    total_count += 1
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}, 0

    average_scores = {cat: values["total_score"] / values["count"] for cat, values in categories.items()}
    overall_average = total_score / total_count if total_count > 0 else 0

    return average_scores, overall_average


def print_average_scores(file_path, average_scores, overall_average):
    """
    Print the average scores for each category and the overall average score.

    Args:
        file_path (str): Path to the JSONL file.
        average_scores (dict): Average scores for each category.
        overall_average (float): Overall average score.
    """
    print(f"******* {file_path}\n 每个类别的平均分：")
    for category, avg_score in average_scores.items():
        print(f"{category}: {avg_score:.4f}")

    print(f"总的平均分: {overall_average:.4f}\n")


def main(directory):
    """
    Process all JSONL files in the specified directory.

    Args:
        directory (str): Directory containing the JSONL files.
    """
    file_list = os.listdir(directory)
    for file_name in file_list:
        if file_name.endswith('.jsonl'):
            file_path = os.path.join(directory, file_name)
            average_scores, overall_average = process_jsonl(file_path)
            if average_scores:
                print_average_scores(file_path, average_scores, overall_average)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSONL files and calculate average scores.")
    parser.add_argument("directory", type=str, help="Directory containing the JSONL files.")
    args = parser.parse_args()

    main(args.directory)