# OAN_cleaner.py 

This script performs a basic CCD image reduction pipeline:
Dark subtraction, Flat correction and hot pixels removal.
It is configured for the SBIG ST-2000XM (KAI 2020M) camera at 
Cúpula Pequeña, Observatorio Astronómico Nacional - UN.
If you are using another detector, please change lines 108 to 115 according to your case. 

The image is by default written as field.fit (line 33).
Flats and Darks must be located in separate directories, and this path should be indicated in lines 41 and 76.

The reduced_image.fit is computed using ccdproc,  an Astropy affiliated package for basic data reductions of CCD images. 
It provides the essential tools for processing of CCD images in a framework that provides error propagation and bad pixel 
tracking throughout the reduction process. 

Science FITS -> Dark Subtraction -> Flat Correction -> Hot Pix -> reduced_image.fit

               
<img width="1487" height="610" alt="s1" src="https://github.com/user-attachments/assets/96e7e48b-6001-43e2-bca0-9138ef49185f" />

