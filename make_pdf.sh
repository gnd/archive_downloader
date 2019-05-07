#!/bin/bash
#
# Convert the downloaded jp2 files into jpg and pdf
#
# Prerequisities:
#   - Imagemagick (convert)
#   - poppler-utils (pdfinfo, pdfseparate, pdfunite)
#   - Tesseract
#
# Install prerequisities like:
#   - apt-get install poppler-utils tesseract-ocr imagemagick
#
# Usage:
#   make_pdf.sh <folder> <outfile>
#
# gnd, 2019
###################################################

function check_installed {
    status=`dpkg-query -W -f='${Status}' $1`
    if [[ "$status" = "install ok installed" ]]; then
        return 1
    else
        echo "package $1 not installed."
        exit
    fi
}

# Check if prerequisities installed
check_installed poppler-utils
check_installed imagemagick
check_installed tesseract-ocr

# Check if param set
if [[ -z $1 ]]; then
	echo "Please provide a name of the folder where the jp2 files are"
    echo "Usage: $0 <folder> <outfile>"
	exit
else
    BOOK=$1
fi
if [[ -z $2 ]]; then
	echo "Please provide name of the final pdf outfile"
    echo "Usage: $0 <folder> <outfile>"
	exit
else
    OUT=$2
fi

# check if dir exists
if [[ ! -d $BOOK ]]; then
    echo "Directory $BOOK doesnt exist."
    echo "Usage: $0 <folder>"
    exit
else
    echo "Deleting old jpgs and pdfs (if any) .."
    rm $BOOK/*.jpg
    rm $BOOK/*.pdf

    # Convert .jp2 into .jpg
    echo "Staring conversion .."
    for img in `ls $BOOK|grep jp2`; do
        imgname=`echo $img|sed 's/\.jp2//g'`
        echo "Converting $img .."
        convert $BOOK/$img $BOOK/$imgname.jpg
    done
    echo "Coversion done."

    # OCR .jpgs into single .pdfs
    echo "Starting OCR with Tesseract"
    for img in `ls $BOOK|grep jpg`; do
        imgname=`echo $img|sed 's/\.jpg//g'`
        echo "OCRing $img .."
        tesseract $BOOK/$img -l eng $BOOK/$imgname pdf
    done
    echo "OCR done."

    # Put all pdfs together
    echo "Creating final pdf .."
    pdfunite $BOOK/*.pdf $OUT.pdf
    echo "All done."
fi
