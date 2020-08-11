import csv
import re
from copy import copy
import numpy as np
import math

def makeCSV(source, target):
    ''' read lines from text file '''
    with open(source,'r') as reader:
        lines = reader.readlines()

    ''' remove leading spaces
    remove trailing newlines
    replaces 2 or more spaces with ';'
    splits on ';'
    '''
    lines2 = copy(lines)
    rows = []
    for line in lines:
        line = line.lstrip().replace('\n','')
        line = re.sub('  +',';',line)
        columns = line.split(';')
        # print(columns,len(columns))
        rows.append(columns)
    
    # print("\n\n")

    ''' count max number of columns in any row '''
    maxCols = max(rows, key = lambda col: len(col))
    # print(len(maxCols))

    ''' get values of colStart and colLen for each column in rows with maximum span to be later used for handling span cells
    colData will store tempRows
    tempRows will store 'maxCols' lists as pairs of colStart and colLen
    '''
    
    '''colData contains data of only max size rows
    fullColData contains data of all rows regardless of number of columns
    '''
    colData = []
    for index, row in enumerate(rows):
        if len(row) == len(maxCols):
            tempRow = []
            for word in row:
                colStart = lines2[index].find(word)
                colLen = len(word) + colStart
                tempRow.append([colStart, colLen])
            colData.append(tempRow)
    
    fullColData = []
    for index, row in enumerate(rows):
        tempRow2 = []
        for word in row:
            wordStart = lines2[index].find(word)
            wordEnd = len(word) + wordStart
            tempRow2.append([wordStart, wordEnd])
        fullColData.append(tempRow2)
    

    ''' extract min colStart and max colLen for each column '''
    arrayColData = np.array(colData)
    # arrayFullColData = np.array(fullColData)
    # print(arrayColData)
    # print(arrayColData.shape)
    # print(fullColData)
    # print(arrayFullColData.shape)
    # _, rowLen, rowDepth = arrayColData.shape
    finalColData = np.empty((len(maxCols) + 2,2), dtype = int)
    for col in range(len(maxCols)):
        minColStart = min(arrayColData[:, col, 0])
        maxColLen = max(arrayColData[:, col, 1])
        finalColData[col + 1,0], finalColData[col + 1,1] = minColStart,maxColLen

    ''' setting start of first column as 0'''
    finalColData[0, 0] = -1
    finalColData[0, 1] = -1
    finalColData[-1, 0] = 999
    finalColData[-1, 1] = 999

    # print(finalColData)
    # finalRows = []
    # for index1, row in enumerate(rows):
    #     if len(row) < len(maxCols):
    #         makeRow = []
    #         for index2, word in enumerate(row):
    #             if index2 == 0:
    #                 wordStart, wordEnd = fullColData[index1][index2]
    #                 for colIter0 in range(finalColData.shape[0]):
    #                     if (wordStart >= finalColData[colIter0, 1] ):
    #                         makeRow.append('')
    #             makeRow.append(word)
    #             for colIter1 in range(finalColData.shape[0]):
    #                 if (wordStart >= finalColData[colIter1,1] 
    #                     and wordStart < finalColData[colIter1 + 1,1]):
    #                     for colIter2 in range(finalColData.shape[0]):
    #                         if (wordEnd >= finalColData[colIter2,0]
    #                             and wordEnd < finalColData[colIter2 + 1,1]):
    #                             cellsToAdd = colIter2 - colIter1 - 1
    #                             for cell in range(cellsToAdd):
    #                                 makeRow.append('')
    #         finalRows.append(makeRow)
    #     else:
    #         finalRows.append(row)
    '''latest!'''
    finalRows = []
    for index1, row in enumerate(rows):
        # if len(row) < len(maxCols):
        prevWordEnd = 0
        makeRow = []
        for index2, word in enumerate(row):
            wordStart, wordEnd = fullColData[index1][index2]
            if index2 == 0:
                for colIter0 in range(finalColData.shape[0] - 1):
                    if wordStart >= finalColData[colIter0 + 1,1]:
                        makeRow.append('')
                makeRow.append(word)
            else:
                for colIter0 in range(finalColData.shape[0]):
                    if (finalColData[colIter0,1] < wordStart
                        and finalColData[colIter0,0] >= prevWordEnd):
                        makeRow.append('')
                makeRow.append(word)
                for colIter1 in range(finalColData.shape[0]):
                    if (wordStart >= finalColData[colIter1,1] 
                        and wordStart < finalColData[colIter1 + 1,1]):
                        for colIter2 in range(finalColData.shape[0]):
                            if (wordEnd >= finalColData[colIter2,0]
                                and wordEnd < finalColData[colIter2 + 1,1]):
                                cellsToAdd = colIter2 - colIter1 - 1
                                for cell in range(cellsToAdd):
                                    makeRow.append('')
            prevWordEnd = wordEnd
        finalRows.append(makeRow)
        # else:
        #     finalRows.append(row)
    
    # for index1, row in enumerate(rows):
    #     # if len(row) < len(maxCols):
    #     makeRow = []
    #     for colIter1 in range(finalColData.shape[0]):
    #         for index2, word in enumerate(row):
    #             wordStart, wordEnd = fullColData[index1][index2]
    #             if index2 == 0:
    #                     if wordStart >= finalColData[colIter1,1]:
    #                         makeRow.append('')
    #                 makeRow.append(word)
    #                 if (wordStart >= finalColData[colIter1,1] 
    #                     and wordStart < finalColData[colIter1 + 1,1]):
    #                     for colIter2 in range(finalColData.shape[0]):
    #                         if (wordEnd >= finalColData[colIter2,0]
    #                             and wordEnd < finalColData[colIter2 + 1,1]):
    #                             cellsToAdd = colIter2 - colIter1 - 1
    #                             for cell in range(cellsToAdd):
    #                                 makeRow.append('')
    #         finalRows.append(makeRow)
    
    # for row in finalRows:
    #     print(row,len(row))
    ''' write rows to csv '''
    with open(target, 'w') as out:
        writer = csv.writer(out)
        writer.writerows(finalRows)
