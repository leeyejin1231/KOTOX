dataset = ["KObfus/no_obfus", "KObfus/total", "KObfus/no+obfus"]

tuning_param  = ["learning_rate","train_batch_size","eval_batch_size","nepoch","SEED","dataset"] ## list of possible paramters to be tuned

train_batch_size = [16]
eval_batch_size = [16]
hidden_size = 1024
nepoch = [15]    
learning_rate = [2e-5]

# model_type = "GroNLP/hateBERT"
# model_type = "unitary/multilingual-toxic-xlm-roberta"
model_type = "textdetox/xlmr-large-toxicity-classifier-v2"

SEED = [44]

param = {"dataset":dataset,"learning_rate":learning_rate,"train_batch_size":train_batch_size,"eval_batch_size":eval_batch_size,"hidden_size":hidden_size,"nepoch":nepoch,"dataset":dataset, "SEED":SEED,"model_type":model_type}