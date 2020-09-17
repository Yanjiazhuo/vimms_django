import sys
sys.path.append('../..')

from pathlib import Path

from vimms.DataGenerator import extract_hmdb_metabolite, get_data_source
from vimms.DataGenerator import get_spectral_feature_database
from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Controller import SimpleMs1Controller
from vimms.Common import *
from vimms.Roi import make_roi, RoiToChemicalCreator
from vimms.FeatureExtraction import extract_roi


def download_data_and_preprocess():
    print('#'*10)
    base_dir = os.path.join(os.getcwd(), 'documents/simple_ms1/example_data')
    print(base_dir)
    compound_file = Path(base_dir, 'hmdb_compounds.p')
    hmdb_compounds = load_obj(compound_file)
    if hmdb_compounds is None: # if file does not exist
        print('hmdb_compounds not exist')
        # # download the entire HMDB metabolite database
        url = '/Users/abel/Downloads/hmdb_metabolites.xml'
        compounds = extract_hmdb_metabolite(url, delete=False)
        save_obj(compounds, compound_file)
    else:
        print('Loaded %d DatabaseCompounds from %s' % (len(hmdb_compounds), compound_file))

    # Generate Spectral Feature Database
    filename = None                    # if None, use all mzML files found
    min_ms1_intensity = 0              # min MS1 intensity threshold to include a data point for density estimation
    min_ms2_intensity = 0              # min MS2 intensity threshold to include a data point for density estimation
    min_rt = 0                         # min RT to include a data point for density estimation
    max_rt = 1440                      # max RT to include a data point for density estimation
    bandwidth_mz_intensity_rt = 1.0    # kernel bandwidth parameter to sample (mz, RT, intensity) values during simulation
    bandwidth_n_peaks = 1.0

    mzml_path = Path(base_dir, 'beers', 'fullscan', 'mzML')
    xcms_output = Path(mzml_path, 'extracted_peaks_ms1.csv')
    out_file = Path(base_dir, 'peak_sampler_mz_rt_int_19_beers_fullscan.p')

    ds_fullscan = get_data_source(mzml_path, filename, xcms_output)
    ps = get_spectral_feature_database(ds_fullscan, filename, min_ms1_intensity, min_ms2_intensity, min_rt, max_rt,
               bandwidth_mz_intensity_rt, bandwidth_n_peaks, out_file)
    ps.get_peak(1, 10) # try to sample 10 MS1 peaks

    print('#'*10, 'Load fragmentation data and train spectral feature database')
    mzml_path = Path(base_dir, 'beers', 'fragmentation', 'mzML')
    xcms_output = Path(mzml_path, 'extracted_peaks_ms1.csv')
    out_file = Path(base_dir, 'peak_sampler_mz_rt_int_19_beers_fragmentation.p')
    ds_fragmentation = get_data_source(mzml_path, filename, xcms_output)
    ps = get_spectral_feature_database(ds_fragmentation, filename, min_ms1_intensity, min_ms2_intensity, min_rt, max_rt,
                   bandwidth_mz_intensity_rt, bandwidth_n_peaks, out_file)
    ps.get_peak(1, 10)
    ps.get_peak(2, 10)

    print('#'*10,'d. Extract the ROIs for DsDA Experiments')
    roi_mz_tol = 10
    roi_min_length = 2
    roi_min_intensity = 1.75E5
    roi_start_rt = min_rt
    roi_stop_rt = max_rt

    file_names = Path(base_dir, 'beers', 'fragmentation', 'mzML').glob('*.mzML')
    out_dir = Path(base_dir,'DsDA', 'DsDA_Beer', 'beer_t10_simulator_files')
    mzml_path = Path(base_dir, 'beers', 'fragmentation', 'mzML')
    extract_roi(list(file_names), out_dir, 'beer_%d.p', mzml_path, ps)

    print('#'*10, 'Extract urine ROIs')
    file_names = Path(base_dir, 'urines', 'fragmentation', 'mzML').glob('*.mzML')
    out_dir = Path(base_dir,'DsDA', 'DsDA_Urine', 'urine_t10_simulator_files')
    mzml_path = Path(base_dir, 'urines', 'fragmentation', 'mzML')

    extract_roi(list(file_names), out_dir, 'urine_%d.p', mzml_path, ps)
    print('#'*10, 'finished download_data()')
