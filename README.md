# Stock_Predict_DQN
you can replace the csv files in "dqn_convNet_keras_tensorflow/sample_data" in order to train on your data

run "dqn_convNet_keras_tensorflow/run.sh" to run the project

basic, the program figures out when to buy or sell, when facing the historical data at a time T.

market_dqn is the main algorithm

market_env is where make the csv file into openAI gym 

market_model_builder is where the network constructed

