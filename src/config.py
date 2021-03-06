from transformers import BertModel, BertTokenizer

# special tokens indices in different models available in transformers
TOKEN_IDX = {
    'bert': {
        'START_SEQ': 101,
        'PAD': 0,
        'END_SEQ': 102,
        'UNK': 100
    },
    'xlm': {
        'START_SEQ': 0,
        'PAD': 2,
        'END_SEQ': 1,
        'UNK': 3
    },
    'roberta': {
        'START_SEQ': 0,
        'PAD': 1,
        'END_SEQ': 2,
        'UNK': 3
    },
    'albert': {
        'START_SEQ': 2,
        'PAD': 0,
        'END_SEQ': 3,
        'UNK': 1
    },
}

# 'O' -> No punctuation
# punctuation_dict = {'O': 0, 'COMMA': 1, 'PERIOD': 2, 'QUESTION': 3}
punctuation_dict = {'0O': 0,
                    '0PERIOD': 1,
                    '0COMMA': 2,
                    '0QUESTION': 3,
                    '0COLON': 4,
                    '0SEMICOLON': 5,
                    '0DASH': 6,
                    '0SLASH': 7,
                    '1O': 8,
                    '1PERIOD': 9,
                    '1COMMA': 10,
                    '1QUESTION': 11,
                    '1COLON': 12,
                    '1SEMICOLON': 13,
                    '1DASH': 14,
                    '1SLASH': 15}

# pretrained model name: (model class, model tokenizer, output dimension, token style)
MODELS = {
    'bert-base-uncased': (BertModel, BertTokenizer, 768, 'bert'),
    'bert-large-uncased': (BertModel, BertTokenizer, 1024, 'bert'),
    'bert-base-multilingual-cased': (BertModel, BertTokenizer, 768, 'bert'),
    'bert-base-multilingual-uncased': (BertModel, BertTokenizer, 768, 'bert'),
    # 'xlm-mlm-en-2048': (XLMModel, XLMTokenizer, 2048, 'xlm'),
    # 'xlm-mlm-100-1280': (XLMModel, XLMTokenizer, 1280, 'xlm'),
    # 'roberta-base': (RobertaModel, RobertaTokenizer, 768, 'roberta'),
    # 'roberta-large': (RobertaModel, RobertaTokenizer, 1024, 'roberta'),
    # 'distilbert-base-uncased': (DistilBertModel, DistilBertTokenizer, 768, 'bert'),
    # 'distilbert-base-multilingual-cased': (DistilBertModel, DistilBertTokenizer, 768, 'bert'),
    # 'xlm-roberta-base': (XLMRobertaModel, XLMRobertaTokenizer, 768, 'roberta'),
    # 'xlm-roberta-large': (XLMRobertaModel, XLMRobertaTokenizer, 1024, 'roberta'),
    # 'albert-base-v1': (AlbertModel, AlbertTokenizer, 768, 'albert'),
    # 'albert-base-v2': (AlbertModel, AlbertTokenizer, 768, 'albert'),
    # 'albert-large-v2': (AlbertModel, AlbertTokenizer, 1024, 'albert'),
    'prajjwal1/bert-small': (BertModel, BertTokenizer, 512, 'bert'),
    'DeepPavlov/rubert-base-cased-conversational': (BertModel, BertTokenizer, 768, 'bert'),
    'DeepPavlov/rubert-base-cased-sentence': (BertModel, BertTokenizer, 768, 'bert'),
    'DeepPavlov/rubert-base-cased': (BertModel, BertTokenizer, 768, 'bert'),
    'sberbank-ai/sbert_large_nlu_ru': (BertModel, BertTokenizer, 1024, 'bert'),
    'sberbank-ai/sbert_large_mt_nlu_ru': (BertModel, BertTokenizer, 1024, 'bert'),
    'cointegrated/rubert-tiny': (BertModel, BertTokenizer, 312, 'bert'),
    'cointegrated/LaBSE-en-ru': (BertModel, BertTokenizer, 768, 'bert')
}
