# Reddit Health Advice ChecKer Bot (HACKBot)

## UI

Our user study interface is in `./UI`.

## Model

Our final model is a KNN model with k=3, found in **`./knn_model/model.py`**. The Jupyter notebook `knn_model.ipynb` was used for model development. 

We use data from the (PUBHEALTH dataset)[https://paperswithcode.com/dataset/pubhealth] for training and testing. Model predictions for the test split are contained in `pubhealth_test_predictions.jsonl`

We evaluate the model on the test split of PUBHEALTH. Our evalution script is `evaluate_model_predictions.py`, which can be run using the command `bash evaluate_model_predictions.py`. 

We include some sample health misinformation claims in `example_reddit_comments.txt` and `user_study_examples.csv`.

To print out model predictions (stored in `reddit_comments_predictions.jsonl`) for the claims in `example_reddit_comments.txt`, we using `print_reddit_predictions.py` and the command `bash print_reddit_predictions.sh`. 

