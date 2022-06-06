import os
import pandas as pd
import re

# dir path
dir_path = "LogiQA-dataset-master"
# load all txt file from data dir
txt_files_path = []
for file in os.listdir(dir_path):
    if file.endswith('txt'):  # we should only focus on txt file
        txt_files_path.append(os.path.join(dir_path, file))


def find_end(s: str):
    res = []
    for idx, char in enumerate(s):
        if char == ".":
            if s[idx - 2:idx] != "Mr":
                if idx != len(s) - 1:
                    if s[idx + 1] == ",":
                        continue
                res.append(idx)
        elif char == ";":
            res.append(idx)
    return res


def deep_split(str_sentence: str, sentences: list):
    index = find_end(str_sentence)
    index.insert(0, 0)
    if len(index) > 1:
        for i in range(len(index) - 1):
            start = index[i]
            end = index[i + 1]
            t = str_sentence[start:end + 1].lstrip('.')
            if re.match("^[ABCDEFGH]\.", t) is not None:
                continue
            t = re.sub("^(; )", "", t)
            if len(t) > 1:
                sentences.append(t)
    else:
        sentences.append(str_sentence)


# read content from each file and store the file into a variable
def read_question(txt_file):
    """a function for read a txt file and return a list contain all content in txt file
    :param txt_file: a txt file path
    :return list[question]
    """
    raw_content = ""
    with open(txt_file, encoding='utf-8') as f:
        for line in f.readlines():
            if len(line.strip()) > 1:
                line = line.strip().replace('"', "")
                raw_content += line.strip() + " "
    sentences = []
    sub_sentence = []
    for word in raw_content.split():
        if word.endswith('.') or word.endswith("?") or word.endswith(':'):
            sub_sentence.append(word)
            str_sentence = " ".join(sub_sentence)
            deep_split(str_sentence, sentences)
            sub_sentence = []
        else:
            sub_sentence.append(word)
    if len(sub_sentence) != 0:
        str_sentence = " ".join(sub_sentence)
        deep_split(str_sentence, sentences)
    return sentences


all_content = []
for t_file in txt_files_path:
    all_content.extend(read_question(t_file))

key_word = ['once', 'although', 'though', 'but', 'because', ' nevertheless', 'before', 'for example', 'until', 'if',
            'previously","when","and", "so", "then", "while", "as long as", "however", "also', "after", "separately",
            "still", "so that", 'or', "moreover", "in addition", 'instead', 'on the other hand', "as", "for instance",
            "nonetheless", 'unless', "meanwhile", 'yet, "since", "rather", "in fact", "indeed', 'later', 'ultimately',
            'as a result', 'either or', 'therefore', 'in turn', 'thus', 'in particular', 'further', 'afterward',
            'next', 'similarly', 'besides', 'if and when', "nor", 'alternatively', 'whereas', 'overall',
            'by comparison', 'till', 'in contrast', 'finally', " otherwise", 'as if', 'thereby', "now that",
            "before and after", "additionally", "meantime", 'by contrast', 'if then', 'likewise', 'in the end',
            'regardiless', "thereafter", 'earlier', 'in other words', 'as soon as', 'except', 'in short', "neither nor",
            "furthermore", "lest", "as though", 'specifically', 'conversely', 'consequently', "as well", "much as",
            'plus', "and", 'hence", "by then', "accordingly", "on the contrary", "simultaneously", "for", "in sum",
            "when and if", "insofar as", "else", "as an alternative", "on the one hand on the other hand"]
special_key = ['if then', 'either or', 'neither or']
one_word_key = [key for key in key_word if " " not in key]
other_word_key = [key.split(' ') for key in key_word if " " in key]

# find the sentences contain keyword
result = []
duplicate = set()
for question in all_content:
    question = question.strip().strip('"')
    question = re.sub("^(\(\d+ *\))", "", question)
    question = re.sub("^[ABCDEFGH]\.", "", question).strip().strip(")").strip().strip("(").strip()
    question = re.sub("^!+", "", question).strip()
    question = re.sub("^(, )", "", question)
    question = re.sub("^([1234567890]\))", "", question).strip()
    question = re.sub("^(`+)", "", question).strip()
    if question in duplicate:
        continue
    duplicate.add(question)
    lower_question = question.lower().split()
    contain_key = []
    for key in one_word_key:
        if key in lower_question:
            contain_key.append(key)
    for key in other_word_key:
        if len(key) > len(lower_question):
            continue
        for idx in range(0, len(lower_question) - len(key)):
            if lower_question[idx:idx + len(key)] == key:
                contain_key.append(" ".join(key))
                break

    for spe in special_key:
        w0, w1 = spe.split()
        if w0 in question and w1 in question:
            if spe.index(w0) < spe.index(w1):
                if spe not in contain_key:
                    contain_key.append(spe)
    if len(contain_key) != 0:
        result.append((question, contain_key))
# keep result to xlsx file
result = pd.DataFrame(result, columns=['sentence', 'keyword'])
result.to_csv("result.csv", index=False)
