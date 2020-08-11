import csv
import re
from copy import deepcopy
import math

def resetRow(rowify, maxCols):
    rowify.clear()
    for _ in range(maxCols):
        rowify.append('')


def makeCSV(source, target):
    ''' read lines from text file '''
    with open(source, 'r') as reader:
        lines = reader.readlines()

    # lines2 = copy(lines)
    rows = []
    for line in lines:
        '''seperate chunks seperated by more than 1 space by ;'''
        tempLine = re.sub('  +','¿',line)
        '''remove trailing whitespaces and newline'''
        tempLine = tempLine.replace('\n','')
        '''split by ¿'''
        words = tempLine.split('¿')
        '''remove empty words'''
        words = list(filter(lambda x: x != '', words))
        # print(words)
        rows.append(words)
    
    
    # print(rows)
    
    ''' count max number of columns in any row '''
    maxCols = len(max(rows, key = len))
    # print("Maxcols:",maxCols)
    maxColRowIndex = max(index for index, row in enumerate(rows) if len(row) == maxCols)

    # print("maxColRowIndex:",maxColRowIndex)
    '''Make column template'''
    ''' list of index of column centers with index referencing the columns'''
    template = []

    cursor = 0
    for word in rows[maxColRowIndex]:
        tempIndex = lines[maxColRowIndex][cursor:].find(word) + cursor
        template.append(tempIndex + int((len(word) - 1)/2))
        cursor = tempIndex + len(word)
    
    # print("template:", template)
    
    columnify = []
    rowify = []

    # print("rows:")
    for rowIndex, row in enumerate(rows):
        '''cursor to keep track of what part of string has already been searched. This makes it possible to avoid duplicate matching'''
        cursor = 0
        '''initialise rowify with maxCols empty words'''
        resetRow(rowify, maxCols)
        for word in row:
            tempIndex = lines[rowIndex][cursor:].find(word) + cursor
            tempCenter = tempIndex + int((len(word) - 1)/2)
            cursor = tempIndex + len(word)
            colIndex = template.index(min(template, key = lambda x:abs(x - tempCenter)))
            rowify[colIndex] = word
            # print(word, tempIndex, tempCenter, cursor)
        columnify.append(deepcopy(rowify))
        # print(rowify)
    '''remove empty rows'''
    resetRow(rowify, maxCols)
    columnify = list(filter(lambda row: row != rowify, columnify))
    

    ''' write rows to csv '''
    with open(target, 'w') as out:
        writer = csv.writer(out)
        writer.writerows(columnify)
