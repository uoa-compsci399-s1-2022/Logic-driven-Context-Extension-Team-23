"""
The author：Xunfeng Cai (upi: xcai720)
            Jituan Wang (upi: jwan370)

Xunfeng and Jituan are in charge of the two databases of "BBC" and "RACE", and
the following codes are all completed by my cooperation with him.
"""

import csv
import os
import traceback
from itertools import compress
import re



def run(rootdir, kw, kw2):
    files = traverse_read_txt(rootdir)
    result = extract_sentence_contains_kw(files, kw=explicit_connectives, kw2=discrete_connectives)
    return result



def traverse_read_txt(rootdir):
    """
    Since the BBC and RACE databases contain a large number of TXT files, and these TXT files are stored
    under different folder categories, we wrote this code to traverse the folder path to find all files
    ending in TXT, so as to avoid missing some data.
    Parameters: rootdir
    由于BBC和RACE的数据库里包含了大量的txt文件，并且这些txt文件都分别存放于不同的文件夹类别下面，所以我们写了这一段代码
    来遍历文件夹路径寻找所有以txt结尾的文件，这样避免了漏掉一些数据。
    参数: rootdir - 数据库路径
    """

    path_list = []
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            file_path = subdir + os.sep + file

            if file_path.endswith(".txt"):
                path_list.append(file_path)
    return path_list



def extract_sentence_contains_kw(files, kw, kw2):
    """
    Go through all the TXT files to find the sentences that contain the keywords.
    Parameters: files - txt File list
                kw and kw2 - Keywords
    遍历所有txt文件，找出包含关键词的句子
    参数:files - txt文件列表
        kw and kw2 - 关键词
    """

    title = []
    result = []
    dir = []
    keyword = []
    for i in range(len(files)):
        try:
            with open(files[i], encoding='utf8', errors='ignore') as f:
                contents = f.readlines()

            content = ' '.join(contents[1:]).replace('\n', '').replace('\\\'', '\'')
            #sentences = content.split(". ")
            sentences = split_into_sentences(content)
            for sentence in sentences:
                if len(sentence.split()) <= 10:
                    continue
                if "?" in sentence:
                    continue
                sentence = sentence.lower()

                if (any(map(lambda word: word in sentence, kw))):
                    title.append(contents[0])
                    result.append(sentence)
                    dir.append(files[i])
                    keyword.append(list(compress(kw, map(lambda word: word in sentence, kw))))

                for special_kw in kw2:
                    if all(x in sentence for x in special_kw):
                        title.append(contents[0])
                        result.append(sentence)
                        dir.append(files[i])
                        kew_word = special_kw[0] + " " + special_kw[1]
                        keyword.append([kew_word])

        except Exception as e:
            print('Error: ', files[i])
            traceback.print_exc()
            pass

    #r = pd.DataFrame({"result": result, "dir": dir, "kw": keyword})
    #print(r)

    final_re = []
    for i in range(len(result)):
        final_re.append([result[i], keyword[i]])

    return final_re



def split_into_sentences(text):
    alphabets = "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences




if __name__ == '__main__':
    """
    The main function.(主函数。）
    """

    # Very critical!
    # Modify your path here. Write the database location in rootdir.
    # This is the first step you need to take to run the code.
    # 非常关键！
    # 在这里修改你的路径。在rootdir里写入数据库所在的位置。
    # 这是你运行这个代码所需要进行的第一步。
    rootdir = "/Users/caixunfeng/Desktop/BBC_Compsci_399_Project/BBC"

    """
    Two kinds of keywords are distinguished here, one is the one that appears directly 
    in the sentence we need(explicit_connectives), and the other is the one that requires 
    special judgment and processing(discrete_connectives).
    这里区分了两种关键词，一种是直接出现在我们需要的句子里面（explicit_connectives），另一种
    是需要进行特别判断和处理的关键词（discrete_connectives）。
    """
    explicit_connectives = ['once', 'although', 'though', 'but', 'because', 'nevertheless', 'before', 'for example',
                            'until', 'if',
                            'previously', 'when', 'and', 'so', 'then', 'while', 'as long as', 'however', 'also',
                            'after', 'separately',
                            'still', 'so that', 'or', 'moreover', 'in addition', 'instead', 'on the other hand', ' as ',
                            'for instance',
                            'nonetheless', 'unless', 'meanwhile', 'yet', 'since', 'rather', 'in fact', 'indeed',
                            'later', 'ultimately',
                            'as a result', 'therefore', 'in turn', 'thus', 'in particular', 'further', 'afterward',
                            'next', 'similarly', 'besides', 'if and when', 'nor', 'alternatively', 'whereas',
                            'over all',
                            'by comparison', 'till', 'in contrast', 'finally', 'otherwise', 'as if', 'thereby',
                            'now that',
                            'before and after', 'additionally', 'meantime', 'by constrast', 'if then', 'likewise',
                            'in the end',
                            'regardless', 'thereafter', 'earlier', 'in other words', 'as soon as', 'except', 'in short',
                            'furthermore', 'lest', 'as though', 'specifically', 'conversely',
                            'consequently', 'as well', 'much as', 'plus', 'and', 'hence', 'by then', 'accordingly',
                            'on the contrary', 'simultaneously', 'for', 'in sum', 'when and if', 'insofar as',
                            'else', 'as an alternative']

    explicit_connectives = list(map(lambda x: " " + x + " ", explicit_connectives))

    discrete_connectives = [['either', 'or'], ['on the one hand', 'on the other hand'],
                            ['neither', 'nor'], ['if', 'then']]

    final_result = run(rootdir, explicit_connectives, discrete_connectives)

    """
    Generate CSV files in the same folder.
    在相同的文件夹下生成csv文件。
    """

    with open('BBC.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(final_result)

    print('Finish')