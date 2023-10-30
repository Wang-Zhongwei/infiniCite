from transformers import AutoTokenizer, AutoModel

def load_specter_models():
    # load model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")

    # load base model
    model = AutoModel.from_pretrained("allenai/specter2_base")

    # load the adapter(s) as per the required task, provide an identifier for the adapter in load_as argument and activate it
    model.load_adapter(
        "allenai/specter2_adhoc_query", source="hf", load_as="adhoc_query", set_active=True
    )
    return tokenizer, model

tokenizer, model = load_specter_models()