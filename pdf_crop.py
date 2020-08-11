from PyPDF2 import PdfFileWriter, PdfFileReader
from copy import copy

''' source is directory of source file.

target is directory of target file.

tables is a dictionary of coordinates 

coordinates is a list of "values"
"values" as  list of 4 values (left,bottom,right,top)
'''
def crop(source, target, tables):
    # print(tables)
    index = 0
    pdf = PdfFileReader(open(source,'rb'))
    for pageNum, coordinates in tables.items():
        page = pdf.getPage(pageNum)
        for value in coordinates:
            # print(value)
            output = PdfFileWriter()
            temp = copy(page)
            bottomLeft = (value[0], value[1])
            topRight = (value[2], value[3])
            temp.trimBox.lowerLeft = bottomLeft
            temp.trimBox.upperRight = topRight
            temp.cropBox.lowerLeft = bottomLeft
            temp.cropBox.upperRight = topRight
            temp.mediaBox.lowerLeft = bottomLeft
            temp.mediaBox.upperRight = topRight
            output.addPage(temp)
            targetSpec = target + '/' + str(pageNum) + '_' + str(index) + '.pdf'
            outfile = open(targetSpec,'wb')
            output.write(outfile)
            outfile.close
            del output
            index = index + 1
    
    
