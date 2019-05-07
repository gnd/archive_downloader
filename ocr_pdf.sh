#!/bin/bash
#
# This script docomposes a given PDF into jpg files,
# OCR's them and puts them back into a searchable PDF.
# The result might be a much bigger PDF with less quality
# but now it is possible to copy, search and mark it.
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
#   ocr_pdf.sh <infile> <outfile>
#
# gnd, 2019
#####################################################

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
	echo "Please provide a input file and an output file."
    echo "Usage: $0 <infile> <outfile>"
	exit
else
    in=$1
fi
if [[ -z $2 ]]; then
    echo "Please provide a input file and an output file."
    echo "Usage: $0 <infile> <outfile>"
	exit
else
    out=$2
fi

# Simple check if input file is a PDF
res=`file $in|grep PDF|wc -l`
if [ "$res" -ne "1" ]; then
    echo "Input file not a PDF."
    exit
fi

# Do the magic
rnd=`openssl rand -hex 2`
pdf_dir="/tmp/inpdf_"$rnd
jpg_dir="/tmp/injpg_"$rnd
out_dir="/tmp/outpdf_"$rnd
mkdir -p $pdf_dir
mkdir -p $jpg_dir
mkdir -p $out_dir

echo "Separating PDF.."
pdfseparate -f 1 $in $pdf_dir"/%d.pdf"
echo "Done."

echo "Converting to JPGs.."
for k in `ls $pdf_dir|grep pdf`; do
    convert -density 150 -quality 80 $pdf_dir/$k $jpg_dir/$k.jpg
done
echo "Done."

echo "OCR-ing the files.."
for k in `ls $jpg_dir|grep jpg`; do
    tesseract $jpg_dir/$k -l eng $out_dir/$k pdf
done
echo "Done."

echo "Putting the OCR'd PDF together.."
pdfunite $out_dir/*.pdf $out
echo "Done."

#rm -rf $pdf_dir
#rm -rf $jpg_dir
#rm -rf $out_dir
