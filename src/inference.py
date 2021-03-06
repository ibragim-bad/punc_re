import re
import torch
import os

import argparse
from model import DeepPunctuation, Student
from config import *
from datetime import datetime
import json
from yttm import YTTM
from lstm_model import BiLSTM_CNN_CRF
from pqrnn import PQRNN

parser = argparse.ArgumentParser(description='Punctuation restoration inference on text file')
parser.add_argument('--cuda', default=True, type=lambda x: (str(x).lower() == 'true'), help='use cuda if available')
parser.add_argument('--pretrained-model', default='xlm-roberta-large', type=str, help='pretrained language model')
parser.add_argument('--lstm-dim', default=-1, type=int,
                    help='hidden dimension in LSTM layer, if -1 is set equal to hidden dimension in language model')
parser.add_argument('--use-crf', default=False, type=lambda x: (str(x).lower() == 'true'),
                    help='whether to use CRF layer or not')
parser.add_argument('--language', default='en', type=str, help='language English (en) oe Bangla (bn)')
parser.add_argument('--in-file', default='data/test_en.txt', type=str, help='path to inference file')
parser.add_argument('--weight-path', default='xlm-roberta-large.pt', type=str, help='model weight path')
parser.add_argument('--sequence-length', default=256, type=int,
                    help='sequence length to use when preparing dataset (default 256)')
parser.add_argument('--out-file', default='data/test_en_out.txt', type=str, help='output file location')
parser.add_argument('--student', default='bert-small.json', type=str, help='student config')
parser.add_argument('--yttm', default='false', type=str, help='yttm model')
parser.add_argument('--pqrnn', default=False, type=bool, help='pqrnn')
args = parser.parse_args()

# tokenizer
if args.yttm == 'false':
    tokenizer = MODELS[args.pretrained_model][1].from_pretrained(args.pretrained_model)
else:
    tokenizer = YTTM(args.yttm)
# tokenizer = MODELS[args.pretrained_model][1].from_pretrained(args.pretrained_model)
token_style = MODELS[args.pretrained_model][3]

# logs
#model_save_path = args.weight_path
st_model_save_path = args.weight_path
# Model
device = torch.device('cuda' if (args.cuda and torch.cuda.is_available()) else 'cpu')
if args.yttm == 'false':
    deep_punctuation = DeepPunctuation(args.pretrained_model, lstm_dim=args.lstm_dim)
else:
    if args.pqrnn:
        deep_punctuation = PQRNN()
    else:
        deep_punctuation = BiLSTM_CNN_CRF(4, tokenizer.vocab_size, 512)



# deep_punctuation.to(device)

with open(args.student) as f:
    cfg = json.load(f)

#deep_punctuation = Student(cfg)
deep_punctuation.to(device)

def postprocess_result(txt):
    txt = ''.join([txt[0].upper(), txt[1:]])
    
    if txt[-2] in ',:\-???.!;?':
        txt = txt[:-2] + '.'
    else:
        txt = txt[:-1] + '.'

    txt = txt.replace('??????????????', '??????????????')

    return txt


def inference():
    deep_punctuation.load_state_dict(torch.load(st_model_save_path, map_location=torch.device(device)))
    deep_punctuation.eval()

    with open(args.in_file, 'r', encoding='utf-8') as f:
        text = f.read()
    text = re.sub(r"[,:\-???.!;?]", '', text)
    print(len(text))
    print(len(text.split()))

    bos = '<BOS>'
    eos = '<EOS>'
    pad = '<PAD>'
    unk = '<UNK>'
    if not args.pqrnn:
            bos = TOKEN_IDX[token_style]['START_SEQ']
            eos = TOKEN_IDX[token_style]['END_SEQ']
            pad = TOKEN_IDX[token_style]['PAD']
            unk = TOKEN_IDX[token_style]['UNK']


    words_original_case = text.split()
    words = text.lower().split()
    words = words

    word_pos = 0
    sequence_len = args.sequence_length
    result = ""
    decode_idx = 0
    
    punctuation_map = {0: '',
                        1: '.',
                        2: ',',
                        3: '?',
                        4: ':',
                        5: ';',
                        6: '-',
                        7: '\n',
                        8: '',
                        9: '.',
                        10: ',',
                        11: '?',
                        12: ':',
                        13: ';',
                        14: '-',
                        15: '\n'}
    capit_idx= len(punctuation_map)//2

    while word_pos < len(words):
        x = [bos]
        y_mask = [0]

        a = datetime.now()
        while len(x) < sequence_len and word_pos < len(words):
            tokens = tokenizer.tokenize(words[word_pos])
            if len(tokens) + len(x) >= sequence_len:
                break
            else:
                for i in range(len(tokens) - 1):
                    x.append(tokenizer.convert_tokens_to_ids(tokens[i]))
                    y_mask.append(0)
                x.append(tokenizer.convert_tokens_to_ids(tokens[-1]))
                y_mask.append(1)
                word_pos += 1
        x.append(eos)
        y_mask.append(0)
        if len(x) < sequence_len:
            x = x + [pad for _ in range(sequence_len - len(x))]
            y_mask = y_mask + [0 for _ in range(sequence_len - len(y_mask))]
        attn_mask = [1 if token != pad else 0 for token in x]

        x = torch.tensor(x)
        y_mask = torch.tensor(y_mask)
        attn_mask = torch.tensor(attn_mask)
        x, attn_mask, y_mask = x.to(device), attn_mask.to(device), y_mask.to(device)
        b = datetime.now()
        print('tokenize')
        print(b - a)
        
        with torch.no_grad():
            if args.use_crf:
                y = torch.zeros(x.shape[0])

                y_predict = deep_punctuation(x, attn_mask, y)
                y_predict = y_predict.view(-1)
            else:
                c = datetime.now()
                y_predict = deep_punctuation(x, attn_mask)
                y_predict = y_predict.view(-1, y_predict.shape[2])

                # y_predict = torch.nn.functional.softmax(y_predict)

                # threshold = torch.tensor([[0.5, 0.75, 0.75, 0.35, 0.35, 0.35, 0.35,0.35,
                #                             0.5, 0.75, 0.75, 0.35, 0.35, 0.35, 0.35, 0.35]]*len(y_predict))
                
                # Zeros = torch.zeros(y_predict.size())
                # y_predict = torch.where(y_predict > threshold, y_predict, Zeros)

                y_predict = torch.argmax(y_predict, dim=1).view(-1)
                d = datetime.now()
                print(f'words len {len(words)}')
                print('model')
                print(d - c)
        for i in range(y_mask.shape[0]):
            if y_mask[i] == 1:
                word = words_original_case[decode_idx] 
                
                if y_predict[i].item() >= capit_idx:
                    word = word.capitalize()
                punc = punctuation_map[y_predict[i].item()]
                if punc !='\n':
                    punc = punc + ' '
                else:
                    punc = '.' + punc

                result += word + punc
                decode_idx += 1
    # print('Punctuated text')
    # print(result)
    result = postprocess_result(result)

    with open(args.out_file, 'w', encoding='utf-8') as f:
        f.write(result)


if __name__ == '__main__':
    inference()
