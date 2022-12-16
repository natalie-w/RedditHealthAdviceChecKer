import json
import argparse
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(description="Print reddit predictions.")

    parser.add_argument(
        "--input_file",
        type=str,
        default=None,
        help="JSONL containing predictions.",
        required=True
    )

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    data = []
    with open(args.input_file) as f:
        for line in f:
            data.append(json.loads(line))

    for prediction in data:
        original_statement = prediction['input_text']
        print(f"INPUT: {original_statement.strip()}")
        label_dict = prediction['label_dict']
        score_dict = prediction['score_dict']

        for similar_sentence in label_dict:
            label = label_dict[similar_sentence]
            scores = score_dict[similar_sentence]
            avg_score = sum(scores) / float(len(scores))
            avg_score_as_percentage = int(avg_score * 100)
            print(f'  **{label.upper()}** {similar_sentence}  ({avg_score_as_percentage}%)')
        print("\n\n")


if __name__=="__main__":
    main()
