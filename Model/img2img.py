from emotions import *
from text_emotion.match_sentences import *
from detectation.ocr import ocr
import cv2
import sys, getopt
import os
import time

def draw_text(img_path, text, out_path):

    bk_img = cv2.imread(img_path)
    sp = bk_img.shape

    # font info settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_sickness = 3

    # get text size
    text_size = cv2.getTextSize(text, font, font_scale, font_sickness)

    if text_size[0][0] > sp[1]:
        len1 = int(len(text)*sp[1]/text_size[0][0])
        while(text[len1]!=' '):
            len1 = len1 - 1
        text1 = text[:len1]
        text2 = text[len1+1:]

        text_size1 = cv2.getTextSize(text1, font, font_scale, font_sickness)
        coord_x_1 = int((sp[1]-text_size1[0][0])/2)
        coord_y_1 = sp[0]-2*text_size1[1]-text_size1[0][1]

        cv2.putText(bk_img, text1, (coord_x_1, coord_y_1), font, font_scale, (255, 255, 255), font_sickness)

        text_size2 = cv2.getTextSize(text2, font, font_scale, font_sickness)
        coord_x_2 = int((sp[1]-text_size2[0][0])/2)
        coord_y_2 = sp[0]-text_size2[1]

        cv2.putText(bk_img, text2, (coord_x_2, coord_y_2), font, font_scale, (255, 255, 255), font_sickness)

    else:
        coord_x = int((sp[1]-text_size[0][0])/2)
        coord_y = sp[0]-text_size[1]

        cv2.putText(bk_img, text, (coord_x, coord_y), font, font_scale, (255, 255, 255), font_sickness)

    cv2.imwrite(out_path, bk_img)

def img2text(img_path):

    print('.'*100)
    print('step 1: ocr')
    # step 1: from image to text_list
    ## input : img_path
    ## output : chat list for chats

    other_chats = ocr(img_path)
    f = open('tmp/input.txt','w')
    str_ = ""
    for line in other_chats:
        line = line.replace("\n","")
        str_ = line + ' ' + str_
    f.write(str_)
    f.close()

    print('.'*100)
    print('step 2: chat_bot')
    # step 2: from text_list to text
    ## input : chat_list
    ## output : prediced reply : one sentence
    os.system("python yzy/OpenNMT/onmt/bin/translate.py -model yzy/OpenNMT/dialog_acc_39.74_ppl_26.63_e13.pt -src tmp/input.txt -output tmp/output.txt -replace_unk -min_length 8")

    f = open('tmp/output.txt','r')
    my_text = f.readline()
    f.close()

    return my_text

def text2img(input_text):
    print('step 3: generate stickers from input text')
    # step 3: from input_text to 3 stickers
    ## input: input_text
    ## output: 3 pairs of stickers

    corpus_dir = '/root/text_emotion/corpus.csv'
    text = input_text

    t = time.time() # timestamp to name the pics

    img_candidates = []

    not_duplicate = []
    query_sentiment_vector, similar_sentences, similar_sentiment_vectors = match_sentences(text, corpus_dir)
    img_set = search(query_sentiment_vector, topK = 3)
    img0 = ""
    for img in img_set:
        if img not in not_duplicate:
            not_duplicate.append(img)
            img0 = img
            break
    outimg = 'tmp/' + str(t) + '_0.jpg'
    print(img0)
    img0 = draw_text(img0, text, outimg)
    img_candidates.append(outimg)

    for i in range(2):
        outimg = 'tmp/' + str(t) + '_' + str(i+1) + '.jpg'
        img_set = search(similar_sentiment_vectors[i], topK = 3)
        img1 = ""
        for img in img_set:
            if img not in not_duplicate:
                not_duplicate.append(img)
                img1 = img
                break
        print(img1)
        draw_text(img1, similar_sentences[i], outimg)
        img_candidates.append(outimg)

    return img_candidates
    
def img2img(img_path, input_text):
    text = img2text(img_path)
    return text2img(input_text), text2img(text)


if __name__ == "__main__":
    img_path = 'ocr/detectation/data/demo/w.jpeg'
    input_text = 'I am very very happy'
    imgpairs1, imgpairs2 = img2img(img_path, input_text)
    print('-'*20)
    print('First Group: ')
    print(imgpairs1)
    print('\nSecond Group: ')
    print(imgpairs2)
