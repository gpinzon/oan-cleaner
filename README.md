oan.cleaner is a tool for reducing the image field.fit (line 33) obtained with the SBIG ST-2000XM ("ST-2K") that 
uses a Kodak KAI-2020M CCD. If you are using another detector, please change lines 108 to 115 according to your case. 
Flats and Darks must be located in separate directories, and this path should be indicated in lines 41 and 76.

The reduced_image.fit is computed using ccdproc,  an Astropy affiliated package for basic data reductions of CCD images. 
It provides the essential tools for processing of CCD images in a framework that provides error propagation and bad pixel 
tracking throughout the reduction process. 


