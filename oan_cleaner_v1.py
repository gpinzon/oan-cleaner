#######################################################
# OAN_Cleaner.py                                      #
# Giovanni Pinzon gapinzone@unal.edu.co               #
# Observatorio Astronómico Nacional - UN              #
#######################################################

import glob
import os
import numpy as np
import ccdproc
import astroscrappy
from astropy import units as u
from astropy.nddata import fits_ccddata_reader
from astropy.io import fits
import matplotlib.pyplot as plt


# ============================================================
# 0. ENABLE OVERWRITING OF MASTERFLAT AND MASTERDARK
# ============================================================
for f in glob.glob('master*.fits') + glob.glob('bpm.fits'):

    try:
        os.remove(f)
    except FileNotFoundError:
        pass


# ============================================================
# 1. READ SCIENCE IMAGE
# ============================================================
data = fits_ccddata_reader('field.fit', hdu=0, unit="adu")

if 'EXPTIME' not in data.header:
    data.header['EXPTIME'] = 5

# ============================================================
# 2. BUILD MASTER DARK (with hot pixel correction)
# ============================================================
dir_darks = 'DARKS_10_23_2026/5/'
archivos = glob.glob(dir_darks + '*.fit')

DarkImages = []
for fits_path in archivos:
    D = fits_ccddata_reader(fits_path, hdu=0, unit="adu")
    DarkImages.append(D)

print(f"Loaded {len(DarkImages)} dark frames.")

# Build hot-pixel mask ONCE from the full stack
stack = np.stack([D.data for D in DarkImages])
med   = np.median(stack, axis=0)
std   = np.median(np.std(stack, axis=0))
hot_mask = med > (np.median(med) + 5 * std)
print(f"Hot pixels flagged: {hot_mask.sum()}")

# Clean each dark
for D in DarkImages:
    D.data[hot_mask] = ccdproc.median_filter(D, size=3).data[hot_mask]

master_dark = ccdproc.combine(DarkImages, output_file='masterdark.fits',
                              overwrite=True, method='average', minmax_clip=True)

# ============================================================
# 3. DARK SUBTRACTION
# ============================================================
dark_subtracted = ccdproc.subtract_dark(data, master_dark,
                                        exposure_time='EXPTIME',
                                        exposure_unit=u.second,
                                        scale=True)

# ============================================================
# 4. BUILD MASTER FLAT (with hot pixel correction)
# ============================================================
dir_flats = 'FLATS_10_23_2026/clear/'
archivos1 = glob.glob(dir_flats + '*.fit')

FlatImages = []
for fits_path in archivos1:
    F = fits_ccddata_reader(fits_path, hdu=0, unit="adu")
    FlatImages.append(F)

print(f"Loaded {len(FlatImages)} flat frames.")

# Clean each flat for hot pixels BEFORE combining
for F in FlatImages:
    F.data[hot_mask] = ccdproc.median_filter(F, size=3).data[hot_mask]

# Normalize each flat to its median, then combine
scaling_func = lambda arr: 1 / np.ma.median(arr)
mf = ccdproc.Combiner(FlatImages)
mf.scaling = scaling_func
master_flat = mf.median_combine()
master_flat.write('masterflat.fits', overwrite=True)

# ============================================================
# 5. FLAT CORRECTION
# ============================================================
reduced_image = ccdproc.flat_correct(dark_subtracted, master_flat)

# ============================================================
# 6. COSMIC RAY + RESIDUAL HOT PIXEL REMOVAL (science frame)
# ============================================================

#The SBIG ST-2000XM ("ST-2K") uses a Kodak KAI-2020M CCD.

cr_mask, cleaned = astroscrappy.detect_cosmics(
    reduced_image.data,
    inmask=hot_mask,      # exclude known hot pixels from CR detection
    sigclip=4.5,
    sigfrac=0.3,
    objlim=5.0,
    gain=0.6,             # electrons/ADU (KAI-2020M, 1600×1200, 7.4 µm)
    readnoise=8.0,        # electrons (KAI-2020M, 1600×1200, 7.4 µm)
    niter=4,
    cleantype='medmask',
    fsmode='median',
)
reduced_image.data = cleaned
print(f"Cosmic rays / bad pixels removed: {cr_mask.sum()}")

# ============================================================
# 7. WRITE OUTPUT
# ============================================================
hdu = fits.PrimaryHDU(data=reduced_image.data, header=data.header)
hdu.writeto('reduced_image.fit', overwrite=True)
print("END")

# ============================================================
# 8. VISUAL COMPARISON
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.set_title('Raw')
ax1.imshow(data.data, interpolation='none', cmap='gray', vmin=0, vmax=7000)
ax2.set_title('Reduced Image')
ax2.imshow(reduced_image.data, interpolation='none', cmap='gray', vmin=0, vmax=7000)
plt.tight_layout()
plt.show()
