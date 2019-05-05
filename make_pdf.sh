#!/bin/bash
#
# Convert the downloaded jp2 files into jpg and pdf
# this needs:
#    - Imagemagick
#    - Imagemagick policy enable write for PDF: https://stackoverflow.com/questions/42928765/convertnot-authorized-aaaa-error-constitute-c-readimage-453/52661288#52661288
#    - Tesseract
#    - pdftk
#
# gnd, 2019
###################################################

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
    pdftk $BOOK/*.pdf cat output $OUT.pdf
    echo "All done."
fi
