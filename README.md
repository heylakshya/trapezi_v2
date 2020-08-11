# Trapezi

A small GUI based utility tool that enables users to extracts tables from text-based PDFs into CSV files.

## Motivation

Anyone who has ever had to deal with tables from a PDF files knows the pain of manual data entry of values. Be it students or researchers trying to compare propertities of various materials from a stack of research papers, converting tabular data to csv can provide many advantages from the spreadsheet world like **search, compare, apply transformations** etc. This can really speed up the workflow of users.

## Screenshots

![Logo](<images/logo.png>)

### The application window

![empty application window](<images/empty.png>)

### Loaded PDF with second selection being made

![selection of second area](<images/selection.png>)

### Appropriately named folder with extracted CSV files

![empty application window](<images/csvfiles.png>)

### The original PDF

![empty application window](<images/originalpdf.png>)

### The Extracted CSV

![empty application window](<images/csvout.png>)

---

## How to use Trapézi

To run the wxpython application

1. Install the dependencies
2. Run the following command in the main.py directory

```bash
    $ pythonw main.py
```

To extract

1. **Open PDF**
2. Navigate to the page with the table you want to extract using either the **Page** textbox or the **« »** buttons
3. Click and drag to mark the area of the table
4. **Add Area** to the Marked Areas list box
5. To delete any selected area from the Marked Areas list box, select the area and click the **Delete Selected Area** button
6. Repeat steps 3 to 5 as required
7. **Extract Tables!**

## Framework

Built with

* Python 3.7.4
* wxpython 4.0.4
* pillow 7.0.0
* matplotlib 3.1.1
* pdf2image 1.13.1
* pypdf2 1.26.0

## Further Improvements

* Support for tables in landscape orientation
* Improve response of selector box
* Support for Windows
* Editable preferences
* Add *About* dialog box
