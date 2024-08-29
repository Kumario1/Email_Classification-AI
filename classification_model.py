from tensorflow import keras
from transformers import TFBertModel, BertConfig, BertTokenizerFast
import tensorflow as tf

new_model = keras.models.load_model('customer_ticket_model_1')

model_name = 'bert-base-uncased'
max_length = 120
config = BertConfig.from_pretrained(model_name)
config.output_hidden_states = False
tokenizer = BertTokenizerFast.from_pretrained(pretrained_model_name_or_path = model_name, config = config)

def classifier(text):
    tokenized_text = tokenizer(
        text=text,
        add_special_tokens=True,
        max_length=max_length,
        truncation=True,
        padding='max_length', 
        return_tensors='tf',
        return_token_type_ids = False,
        return_attention_mask = True,
        verbose = True)
    test_results = new_model.predict([tokenized_text['input_ids'][:10], tokenized_text['attention_mask'][:10]])
    indexes = tf.argmax(test_results['ticket_category'], axis=1)
    val = indexes[0]
    folders = ['Technical issue', 'Billing inquiry', 'Cancellation request', 'Product inquiry', 'Refund request']
    return folders[val]