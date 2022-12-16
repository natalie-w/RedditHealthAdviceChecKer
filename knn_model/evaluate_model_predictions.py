import json
import argparse
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(description="Process eye gaze data.")

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

    total_num_predictions = len(data)
    count_correct_majority_prediction = 0
    count_correct_highest_scoring_prediction = 0

    for prediction in data:
        original_statement_label = prediction['input_text_label']
        similar_statement_truth_list = prediction['label_dict'].values()

        ### Evaluate on ajority vote label
        counter = Counter(similar_statement_truth_list)
        majority_similar_statement_truth_label, count_of_label = counter.most_common()[0]
        if majority_similar_statement_truth_label == original_statement_label:
            count_correct_majority_prediction += 1

        ### Evaluate on highest scoring sentence label
        score_dict = prediction['score_dict']
        highest_score_for_all_sentences = -1
        highest_scoring_sentence = ""
        # Find highest score for each individual similar sentence
        for similar_sentence in score_dict:
            score_list = score_dict[similar_sentence]
            # If max score for the current sentence is greater than any previously seen scores, update highest score
            #   and highest scoring sentence
            max_curr_score = max(score_list)
            if max_curr_score > highest_score_for_all_sentences:
                highest_scoring_sentence = similar_sentence
        # Find label for highest scoring sentence
        label_dict = prediction['label_dict']
        highest_scoring_sentence_label = label_dict[highest_scoring_sentence]
        if highest_scoring_sentence_label == original_statement_label:
            count_correct_highest_scoring_prediction += 1

    print(f"Total number of predictions: {total_num_predictions}")

    majority_vote_accuracy = count_correct_majority_prediction / float(total_num_predictions)
    print(f'MAJORITY VOTE LABEL accuracy: {majority_vote_accuracy}')

    highest_scoring_accuracy = count_correct_highest_scoring_prediction / float(total_num_predictions)
    print(f'HIGHEST SCORING SENTENCE LABEL accuracy: {highest_scoring_accuracy}')


if __name__=="__main__":
    main()
