import numpy as np
import pandas as pd
import pylab as plt
import pymzml

import sys
sys.path.append('../..')

from vimms.Roi import RoiToChemicalCreator, make_roi
from vimms.DataGenerator import DataSource, PeakSampler, get_spectral_feature_database
from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Controller import TopNController
from vimms.Environment import Environment
import matplotlib
matplotlib.pyplot.switch_backend('Agg')
from vimms.PlotsForPaper import count_stuff, plot_num_scans, match_peaklist, check_found_matches, \
plot_matched_intensities, plot_matched_precursors
from vimms.Common import *


def topn_processor():
    pathlist = []
    base_dir = 'documents/simple_ms1/example_data'
    # base_dir = 'example_data'
    mzml_path = os.path.join(base_dir, 'beers', 'fragmentation', 'mzML')
    file_name = 'Beer_multibeers_1_T10_POS.mzML'

    experiment_name = 'mzml_compare'
    experiment_out_dir = os.path.join(base_dir, 'results', experiment_name) 
    min_rt = 0
    max_rt = 1441
    kde_min_ms1_intensity = 0 # min intensity to be selected for kdes
    kde_min_ms2_intensity = 0

    roi_mz_tol = 10
    roi_min_length = 1
    roi_min_intensity = 0
    roi_start_rt = min_rt
    roi_stop_rt = max_rt

    isolation_width = 1   # the (full) isolation width in Dalton around a selected precursor m/z
    ionisation_mode = POSITIVE
    N = 10
    rt_tol = 15
    mz_tol = 10
    min_ms1_intensity = 1.75E5 # minimum ms1 intensity to fragment

    mzml_filename = 'simulated.mzML'
    mzml_out = os.path.join(experiment_out_dir, mzml_filename)
    pathlist.append(mzml_out)

    print('#'*10, 'Train densities')   
    ds = DataSource()
    ds.load_data(mzml_path, file_name=file_name)
    bandwidth_mz_intensity_rt=1.0
    bandwidth_n_peaks=1.0
    ps = get_spectral_feature_database(ds, file_name, kde_min_ms1_intensity, kde_min_ms2_intensity, min_rt, max_rt,
                   bandwidth_mz_intensity_rt, bandwidth_n_peaks)

    print('#'*10, 'Extract all ROIs')
    mzml_file = os.path.join(mzml_path, file_name)
    good_roi, junk = make_roi(mzml_file, mz_tol=roi_mz_tol, mz_units='ppm', min_length=roi_min_length,
                              min_intensity=roi_min_intensity, start_rt=roi_start_rt, stop_rt=roi_stop_rt)
    all_roi = good_roi + junk
    print('#'*10, len(all_roi))

    keep = []
    for roi in all_roi:
        if np.count_nonzero(np.array(roi.intensity_list) > min_ms1_intensity) > 0:
            keep.append(roi)

    all_roi = keep

    set_log_level_debug()
    rtcc = RoiToChemicalCreator(ps, all_roi)
    data = rtcc.chemicals
    save_obj(data, os.path.join(experiment_out_dir, 'dataset.p'))

    set_log_level_warning()
    pbar = True
    mass_spec = IndependentMassSpectrometer(ionisation_mode, data, ps)
    controller = TopNController(ionisation_mode, N, isolation_width, mz_tol,
                                rt_tol, min_ms1_intensity)
    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    # run the simulation
    env.run()
    set_log_level_debug()
    env.write_mzML(experiment_out_dir, mzml_filename)

    print('#'*10, 'Compare Results')
    matplotlib.use('agg')
    simulated_input_file = mzml_out
    simulated_mzs, simulated_rts, simulated_intensities, simulated_cumsum_ms1, simulated_cumsum_ms2 = count_stuff(
        simulated_input_file, min_rt, max_rt)

    real_input_file = mzml_file
    real_mzs, real_rts, real_intensities, real_cumsum_ms1, real_cumsum_ms2 = count_stuff(
        real_input_file, min_rt, max_rt)

    plt.rcParams.update({'font.size': 14})
    out_file = os.path.join(base_dir, 'results', 'topN_num_scans.png')
    pathlist.append(out_file)
    plot_num_scans(real_cumsum_ms1, real_cumsum_ms2, simulated_cumsum_ms1, simulated_cumsum_ms2, out_file)

    mz_tol = None # in ppm. if None, then 2 decimal places is used for matching the m/z
    rt_tol = 5 # seconds
    matches = match_peaklist(real_mzs, real_rts, real_intensities, simulated_mzs, simulated_rts, simulated_intensities, mz_tol, rt_tol)
    check_found_matches(matches, 'Real', 'Simulated')

    mz_tol = None
    rt_tol = 10
    matches = match_peaklist(real_mzs, real_rts, real_intensities, simulated_mzs, simulated_rts, simulated_intensities, mz_tol, rt_tol)
    check_found_matches(matches, 'Real', 'Simulated')

    mz_tol = None
    rt_tol = 15
    matches = match_peaklist(real_mzs, real_rts, real_intensities, simulated_mzs, simulated_rts, simulated_intensities, mz_tol, rt_tol)
    check_found_matches(matches, 'Real', 'Simulated')

    unmatched_intensities = []
    matched_intensities = []
    for key, value in list(matches.items()):
        intensity = key[2]
        if value is None:
            unmatched_intensities.append(intensity)
        else:
            matched_intensities.append(intensity)
    plt.rcParams.update({'font.size': 18})   

    out_file = os.path.join(base_dir, 'results', 'topN_matched_intensities.png')
    plot_matched_intensities(matched_intensities, unmatched_intensities, out_file)
    pathlist.append(out_file)
    out_file = os.path.join(base_dir, 'results', 'topN_matched_precursors.png')
    plot_matched_precursors(matches, 50, 1000, 180, 1260, out_file)
    pathlist.append(out_file)
    return pathlist


