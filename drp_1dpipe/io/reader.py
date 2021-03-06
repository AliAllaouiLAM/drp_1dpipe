import os.path
from pfs.datamodel.drp import PfsObject
from pylibamazed.redshift import (CSpectrumSpectralAxis,
                                  CSpectrumFluxAxis_withError,
                                  CSpectrum)
import numpy as np


def read_spectrum(path):
    """
    Read a pfsObject FITS file and build a CSpectrum out of it

    :param path: FITS file name
    :rtype: CSpectrum
    """

    obj = PfsObject.readFits(path)
    mask = obj.mask
    valid = np.where(mask == 0, True, False)
    wavelength = np.array(np.extract(valid, obj.wavelength), dtype=np.float32)
    flux = np.array(np.extract(valid, obj.flux), dtype=np.float32)
    error = np.array(np.extract(valid, np.sqrt(obj.covar[0][0:])), dtype=np.float32)
    spectralaxis = CSpectrumSpectralAxis(wavelength * 10.0)
    signal = CSpectrumFluxAxis_withError(flux, error)
    spectrum = CSpectrum(spectralaxis, signal)
    spectrum.SetName(os.path.basename(path))
    return spectrum
