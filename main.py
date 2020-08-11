# import wx


# headImage = wx.Image('logo.png', wx.BITMAP_TYPE_ANY)
# headImageBitmap = headImage.Scale(50, 50, wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
# wx.StaticBitmap(panel, id = -1, bitmap = headImageBitmap, pos = (10,10))

import wx
# Used to determine the size of an image
from PIL import Image   

# Use the wxPython backend of matplotlib
import matplotlib       
matplotlib.use('WXAgg')

# Matplotlib elements used to draw the bounding rectangle
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import pdf2image
import os
import shutil
import ast
from datetime import datetime

from pdf_crop import crop
from pdf_text import extractText
from txt_csv2 import makeCSV

class MyDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(MyDialog, self).__init__(parent, title = title, size = (250,100)) 
        self.panel = wx.Panel(self) 
        self.par = parent
        self.message = wx.StaticText(self.panel, -1, label = "The selected tables have not been extracted yet!")
        self.extractbtn = wx.Button(self.panel, -1, label = "Extract")
        self.discardbtn = wx.Button(self.panel, -1, label = "Discard")
        self.buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons.Add(self.extractbtn, 1, wx.ALL, 10)
        self.buttons.Add(self.discardbtn, 1, wx.ALL, 10)
        self.finalSizer = wx.BoxSizer(wx.VERTICAL)
        self.finalSizer.Add(self.message, 1, wx.ALL, 10)
        self.finalSizer.Add(self.buttons, 1, wx.ALL, 10)
        self.extractbtn.Bind(wx.EVT_BUTTON, self.onExtract)
        self.discardbtn.Bind(wx.EVT_BUTTON, self.onDiscard)
        self.panel.SetSizerAndFit(self.finalSizer)
        # self.panel.SetAutoLayout(True)
        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.panel)
        self.SetSizerAndFit(self.sizer)

    def onExtract(self, event):
        self.par.extract(event)
        self.EndModal(-1)
        self.Destroy()

    def onDiscard(self, event):
        self.EndModal(-1)
        self.Destroy()

    # def on_quit_click(self, event):
    #     self.Destroy()

class MainFrame(wx.Frame):
    """Create MainFrame class."""
    def __init__(self, *args, **kwargs):
        if os.path.isdir('_temp'):
            shutil.rmtree('_temp')

        super(MainFrame, self).__init__(None,
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
        )
        self.Title = 'Trapézi'
        # self.SetMenuBar(MenuBar(self))
        # self.ToolBar = MainToolbar(self)
        self.Bind(wx.EVT_CLOSE, self.on_quit_click)
        self.panel = MainPanel(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.panel)
        self.SetSizerAndFit(sizer)
        self.Centre()
        self.Show()

    def on_quit_click(self, event):
        """Handle close event."""
        self.panel.handleExisting()
        self.panel.status_bar.SetLabel('Cleaning Up...')
        if os.path.isdir('_temp'):
            shutil.rmtree('_temp')
        wx.Exit()


class MainPanel(wx.Panel):
    """Panel class to contain frame widgets."""
    def __init__(self, parent, *args, **kwargs):
        super(MainPanel, self).__init__(parent, *args, **kwargs)

        self.areas = dict()
        self.areaList = []
        self.pages = 0
        self.currentPage = 0
        self.pathname = ''
        self.source = ''
        self.imgDir = ''
        self.extracted = False

        """Create and populate main sizer."""
        self.status_bar = wx.StaticText(self, id = -1, size = wx.Size(200, -1))
        self.status_bar.SetLabel('Open File')

        self.headSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttonOpen = wx.Button(self,id = wx.ID_OPEN, label = "Open PDF")
        self.buttonOpen.Bind(wx.EVT_BUTTON, self.openFile)
        self.headSizer.Add(self.buttonOpen, 0, wx.EXPAND|wx.ALL|wx.ALIGN_CENTRE_VERTICAL, 10)

        self.listHeader = wx.StaticText(
            self, 
            -1, 
            "Marked Areas"
        )
        

        self.lb = wx.ListBox(
            self,
            -1
        )
        self.lb.SetMinSize(wx.Size(-1,300))

        self.buttonAdd = wx.Button(self, id = -1, label = "Add Area")
        self.buttonDel = wx.Button(
            self, 
            id = -1, 
            label = "Delete Selected Area"
        )

        self.buttonNext = wx.Button(self, id = -1, label = '»')
        self.buttonPrev = wx.Button(self, id = -1, label = '«')
        self.buttonNext.Bind(wx.EVT_BUTTON, self.pageNext)
        self.buttonPrev.Bind(wx.EVT_BUTTON, self.pagePrev)

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.buttonSizer.Add(self.buttonAdd, 1, wx.ALL, 10)
        self.buttonSizer.Add(self.buttonDel, 1, wx.ALL, 10)

        self.leftSizer = wx.BoxSizer(wx.VERTICAL)

        self.pdfTitleTag = wx.StaticText(
            self,
            -1,
            label = 'PDF Name'
        )
        self.pdfTitle = wx.TextCtrl(
            self, 
            -1, 
            value = '',
            style = wx.TE_READONLY
        )
        self.pdfTitle.SetMinSize(wx.Size(150,-1))
        self.pdfpgnoTag = wx.StaticText(
            self,
            -1,
            label = 'Page '
        )
        self.pdfpgno = wx.TextCtrl(
            self, 
            -1, 
            value = str(0),
            style = wx.TE_PROCESS_ENTER
        )
        self.outof = wx.StaticText(self, -1, label = 'out of ')
        self.pdfTotalPages = wx.StaticText(
            self,
            -1,
            label = str(self.pages)
        )
        self.pdfpgno.SetMinSize(wx.Size(30,-1))
        self.pdfTotalPages.SetMinSize(wx.Size(30,-1))
        self.pdfpgno.Bind(wx.EVT_TEXT_ENTER, self.gotoPage)

        self.headSizer.Add(self.pdfTitleTag, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.pdfTitle, 1, wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.pdfpgnoTag, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.pdfpgno, 0, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.outof, 0, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.pdfTotalPages, 0, wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.buttonPrev, 0, wx.EXPAND|wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)
        self.headSizer.Add(self.buttonNext, 0, wx.EXPAND|wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTRE_VERTICAL, 20)

        self.BigSizer = wx.BoxSizer(wx.VERTICAL)
        self.viewer = wx.StaticBox(self, -1, 'PDF Viewer')
        self.viewer.SetMinSize(wx.Size(500,1000))
        self.rightSizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.selector = rectangleSelection(self)
        self.buttonExtractTables = wx.Button(self, id = -1, label = 'Extract Tables!')


        self.leftSizer.Add(self.buttonSizer, 0, wx.EXPAND)
        self.leftSizer.Add(self.listHeader, 0, wx.EXPAND|wx.LEFT, 10)
        self.leftSizer.Add(self.lb, 1, wx.EXPAND|wx.ALL, 10)

        self.buttonAdd.Bind(wx.EVT_BUTTON, self.addArea)
        self.buttonDel.Bind(wx.EVT_BUTTON, self.delArea)
        self.buttonExtractTables.Bind(wx.EVT_BUTTON, self.extract)


        self.staticSizer = wx.StaticBoxSizer(self.viewer, wx.VERTICAL)
        self.staticSizer.SetMinSize(wx.Size(500,1000))
        self.staticSizer.Add(self.selector, 1, wx.EXPAND|wx.ALL, 10)
        self.rightSizer.Add(self.staticSizer, 1, wx.EXPAND|wx.ALL, 10)

        self.sizer.Add(self.leftSizer, 1, wx.EXPAND)
        self.sizer.Add(self.rightSizer, 2, wx.EXPAND)
        self.BigSizer.Add(self.headSizer, 0, wx.EXPAND)
        self.BigSizer.Add(self.sizer, 1, wx.EXPAND)
        self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomSizer.Add(self.status_bar, 1, wx.EXPAND|wx.ALIGN_LEFT|wx.BOTTOM|wx.LEFT, 10)
        self.bottomSizer.Add(self.buttonExtractTables, 0, wx.ALIGN_RIGHT|wx.BOTTOM|wx.RIGHT, 10)
        self.BigSizer.Add(self.bottomSizer,0, wx.EXPAND)

        self.SetSizer(self.BigSizer)
        self.SetAutoLayout(True)
        self.BigSizer.Fit(self)
    
    def addArea(self, event):
        self.tempArea = []
        self.tempArea.append(int(float(self.selector.coordinatesx0.GetValue())))
        self.tempArea.append(int(float(self.selector.coordinatesy0.GetValue())))
        self.tempArea.append(int(float(self.selector.coordinatesx1.GetValue())))
        self.tempArea.append(int(float(self.selector.coordinatesy1.GetValue())))

        if self.areas.get(int(self.pdfpgno.GetValue())) is None:
            self.areas[int(self.pdfpgno.GetValue())] = []

        self.areas[int(self.pdfpgno.GetValue())].append(self.tempArea)
        self.areaList.append('~'.join([str(self.pdfpgno.GetValue()), str(self.tempArea)]))
        self.lb.Set(self.areaList)
        self.status_bar.SetLabel('Area added')
        # print(self.areas)
    
    def delArea(self, event):
        sel = self.lb.GetSelection()
        print(sel)
        if sel != -1:
            rmPage, rmArea = self.areaList[sel].split('~')
            self.areas[int(rmPage)].remove(ast.literal_eval(rmArea))
            self.lb.Delete(sel)
            self.areaList.pop(sel)
            self.status_bar.SetLabel('Area deleted')

    def handleExisting(self):
        if self.extracted == False and len(self.areaList) != 0 and self.pathname != '':
            dialog = MyDialog(self, "Hold Up!")
            dialog.ShowModal()
            dialog.Destroy()

    def openFile(self, event):
        self.handleExisting()
        self.status_bar.SetLabel('Opening file...')
        with wx.FileDialog(self, "Open PDF file", wildcard="PDF files (*.pdf)|*.pdf", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            self.areas = dict()
            self.areaList = []
            self.currentPage = 0
            self.extracted = False
            self.lb.Set(self.areaList)

            self.pathname = fileDialog.GetPath()
            paths = self.pathname.split('/')
            self.source = paths[-1]
            
            self.pdfTitle.SetValue(self.source)
            self.pdfToImages(self.pathname)

            self.pdfpgno.SetValue(str(self.currentPage))
            self.pdfTotalPages.SetLabel(str(self.pages))
            self.status_bar.SetLabel('Loading View')
            self.updateView()
            
            self.status_bar.SetLabel('Ready')

    def pdfToImages(self, path):
        self.status_bar.SetLabel('Loading PDF...')
        pdfImages = pdf2image.convert_from_path(path, dpi = 72)
        index = 0
        self.imgDir = "_temp/" + self.source[:-4] + "/pageimages"
        if os.path.isdir(self.imgDir):
            shutil.rmtree(self.imgDir)
        os.makedirs(self.imgDir)
        for image in pdfImages:
            image.save(self.imgDir + "/" +"page_" + str(index) +'.jpg')
            index = index + 1
        self.pages = index - 1

    def pageNext(self, evnet):
        if self.currentPage < self.pages:
                self.currentPage = self.currentPage + 1
                self.updateView()

    def pagePrev(self, event):
        if self.currentPage > 0:
                self.currentPage = self.currentPage - 1
                self.updateView()
    
    def gotoPage(self, event):
        page = int(self.pdfpgno.GetValue())
        if page < 0:
            self.currentPage = 0
            self.pdfpgno.SetValue(str(self.currentPage))
            self.updateView()
        elif page > self.pages:
            self.currentPage = self.pages
            self.pdfpgno.SetValue(str(self.currentPage))
            self.updateView()
        else:
            self.currentPage = page
            self.pdfpgno.SetValue(str(self.currentPage))
            self.updateView()
    
    def updateView(self):
        self.selector.setImage(self.imgDir + "/" +"page_" + str(self.currentPage) +'.jpg')
        self.pdfpgno.SetValue(str(self.currentPage))

    def extract(self, event):
        self.status_bar.SetLabel('Setting up directories...')
        cropPrefix = '_temp/' + self.source[:-4] + '/crop'
        txtFile = '_temp/' + self.source[:-4] + '/text'
        noPadtxtFile = '_temp/' + self.source[:-4] + '/nopadtext'
        csvFile = self.pathname[:-4] + '_tables_' + str(datetime.now())[:-7]

        if os.path.isdir(cropPrefix):
            shutil.rmtree(cropPrefix)
        os.makedirs(cropPrefix)

        if os.path.isdir(txtFile):
            shutil.rmtree(txtFile)
        os.makedirs(txtFile)

        if os.path.isdir(noPadtxtFile):
            shutil.rmtree(noPadtxtFile)
        os.makedirs(noPadtxtFile)

        if os.path.isdir(csvFile):
            shutil.rmtree(csvFile)
        os.makedirs(csvFile)

        self.status_bar.SetLabel('Cropping...')
        crop(self.pathname, cropPrefix, self.areas)

        self.status_bar.SetLabel('Extracting Text...')
        for file in os.listdir(cropPrefix):
            extractText(cropPrefix + '/' + file, txtFile + '/' + file[:-4] + '.txt', noPadtxtFile + '/' + file[:-4] + '.txt')

        self.status_bar.SetLabel('Converting to CSV...')
        for file in os.listdir(txtFile):
            makeCSV(txtFile  + '/' + file, csvFile + '/' + file[:-4] + '.csv')
        
        self.status_bar.SetLabel("All Done!")
        self.extracted = True




class rectangleSelection(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent)
        self.figure = plt.figure()
        self.axes = plt.Axes(self.figure, [0,0,1,1])
        self.axes.set_axis_off()
        self.figure.add_axes(self.axes)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.rect = Rectangle((0,0), 1, 1, facecolor='None', edgecolor='red')
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.axes.add_patch(self.rect)

        self.par = parent

        self.coordinatesx0 = wx.TextCtrl(
            self, 
            -1, 
            value = str(self.x0),
            style = wx.TE_READONLY
        )
        self.coordinatesy0 = wx.TextCtrl(
            self, 
            -1, 
            value = str(self.y0),
            style = wx.TE_READONLY
        )
        self.coordinatesx1 = wx.TextCtrl(
            self, 
            -1, 
            value = str(self.x1),
            style = wx.TE_READONLY
        )
        self.coordinatesy1 = wx.TextCtrl(
            self, 
            -1, 
            value = str(self.y1),
            style = wx.TE_READONLY
        )

        self.coordinate = wx.BoxSizer(wx.HORIZONTAL)
        self.coordinate.Add(self.coordinatesx0, 1, wx.ALL, 10)
        self.coordinate.Add(self.coordinatesy0, 1, wx.ALL, 10)
        self.coordinate.Add(self.coordinatesx1, 1, wx.ALL, 10)
        self.coordinate.Add(self.coordinatesy1, 1, wx.ALL, 10)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND|wx.ALL)
        self.sizer.Add(self.coordinate, 0, wx.EXPAND|wx.ALL)
        self.SetSizer(self.sizer)
        self.Fit()

        # Connect the mouse events to their relevant callbacks
        self.canvas.mpl_connect('button_press_event', self._onPress)
        self.canvas.mpl_connect('button_release_event', self._onRelease)
        self.canvas.mpl_connect('motion_notify_event', self._onMotion)

        self.pressed = False

    def _onPress(self, event):
        if event.xdata is not None and event.ydata is not None:

            # Upon initial press of the mouse record the origin and record the mouse as pressed
            self.pressed = True
            self.rect.set_linestyle('dashed')
            self.x0 = event.xdata
            self.y0 = event.ydata

            self.par.status_bar.SetLabel('Marking...')
            


    def _onRelease(self, event):
        '''Callback to handle the mouse being released over the canvas'''

        # Check that the mouse was actually pressed on the canvas to begin with and this isn't a rouge mouse 
        # release event that started somewhere else
        if self.pressed:
            self.par.status_bar.SetLabel('Marked')

            # Upon release draw the rectangle as a solid rectangle
            self.pressed = False
            self.rect.set_linestyle('solid')

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata

            # Set the width and height and origin of the bounding rectangle
            self.boundingRectWidth =  self.x1 - self.x0
            self.boundingRectHeight =  self.y1 - self.y0
            self.bouningRectOrigin = (self.x0, self.y0)

            self.updateCoord()
            

            # Draw the bounding rectangle
            self.rect.set_width(self.boundingRectWidth)
            self.rect.set_height(self.boundingRectHeight)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()


    def _onMotion(self, event):
        '''Callback to handle the motion event created by the mouse moving over the canvas'''

        # If the mouse has been pressed draw an updated rectangle when the mouse is moved so 
        # the user can see what the current selection is
        if self.pressed:
            self.par.status_bar.SetLabel('Marking...')

            # Check the mouse was released on the canvas, and if it wasn't then just leave the width and 
            # height as the last values set by the motion event
            if event.xdata is not None and event.ydata is not None:
                self.x1 = event.xdata
                self.y1 = event.ydata
            
            # Set the width and height and draw the rectangle
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.canvas.draw()


    def setImage(self, pathToImage):
        '''Sets the background image of the canvas'''
        
        # Load the image into matplotlib and PIL
        image = matplotlib.image.imread(pathToImage) 
        imPIL = Image.open(pathToImage) 

        # Save the image's dimensions from PIL
        self.imageSize = imPIL.size
        
        # Add the image to the figure and redraw the canvas. Also ensure the aspect ratio of the image is retained.
        self.axes.imshow(image,aspect='equal') 
        self.canvas.draw()
    
    def updateCoord(self):
        y0 = self.imageSize[1] - self.y0
        y1 = self.imageSize[1] - self.y1
        finalx0 = min(self.x0,self.x1)
        finalx1 = max(self.x0,self.x1)
        finaly0 = min(y0,y1)
        finaly1 = max(y0,y1)

        self.coordinatesx0.SetValue(str(finalx0))
        self.coordinatesy0.SetValue(str(finaly0))
        self.coordinatesx1.SetValue(str(finalx1))
        self.coordinatesy1.SetValue(str(finaly1))


if __name__ == '__main__':
    """Run the application."""
    screen_app = wx.App()
    main_frame = MainFrame()
    screen_app.MainLoop()
