import matplotlib
matplotlib.pyplot.switch_backend('Agg')

import numpy as np
import pandas as pd
import pylab as plt
import pymzml
import math
import seaborn as sns

import sys
sys.path.append('../..')

from vimms.Roi import RoiToChemicalCreator, make_roi
from vimms.DataGenerator import DataSource, PeakSampler, get_spectral_feature_database
from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Controller import TopNController
from vimms.TopNExperiment import get_params, run_serial_experiment, run_parallel_experiment
from vimms.PlotsForPaper import get_df, load_controller, compute_performance_scenario_2
from vimms.Common import *


def varying_topn_processor():
    pathlist = []   
    base_dir = 'documents/simple_ms1/example_data'
    mzml_path = os.path.join(base_dir, 'beers', 'fragmentation', 'mzML')
    file_name = 'Beer_multibeers_1_T10_POS.mzML'

    experiment_name = 'beer1pos'
    url_experiment_out_dir = os.path.join(base_dir, 'results', experiment_name, 'mzML')
    experiment_out_dir = os.path.abspath(os.path.join(base_dir, 'results', experiment_name, 'mzML'))
    min_rt = 3*60 # start time when compounds begin to elute in the mzML file
    max_rt = 21*60
    kde_min_ms1_intensity = 0 # min intensity to be selected for kdes
    kde_min_ms2_intensity = 0

    roi_mz_tol = 10
    roi_min_length = 1
    roi_min_intensity = 0
    roi_start_rt = min_rt
    roi_stop_rt = max_rt

    isolation_window = 1   # the isolation window in Dalton around a selected precursor ion
    ionisation_mode = POSITIVE
    N = 10
    rt_tol = 15
    mz_tol = 10
    min_ms1_intensity = 1.75E5 # minimum ms1 intensity to fragment

    mzml_out = os.path.join(experiment_out_dir, 'simulated.mzML')
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
    print('#'*10, 'How many singleton and non-singleton ROIs =>', len([roi for roi in all_roi if roi.n == 1]))

    keep = []
    for roi in all_roi:
        if np.count_nonzero(np.array(roi.intensity_list) > min_ms1_intensity) > 0:
            keep.append(roi)

    all_roi = keep
    set_log_level_debug()
    rtcc = RoiToChemicalCreator(ps, all_roi)
    data = rtcc.chemicals
    save_obj(data, os.path.join(experiment_out_dir, 'dataset.p'))
    print('#'*10, 'Run Top-N Controller')
    set_log_level_warning()
    pbar = False # turn off progress bar
    Ns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
    rt_tols = [15]
    params = get_params(experiment_name, Ns, rt_tols, mz_tol, isolation_window, ionisation_mode, data, ps, 
                        min_ms1_intensity, min_rt, max_rt, experiment_out_dir, pbar)
    run_serial_experiment(params)


    print('#'*10, 'Analyse Results')
    min_ms1_intensity = 0
    rt_range = [(min_rt, max_rt)]
    mz_range = [(0, math.inf)]
    results_dir = os.path.join(base_dir, 'results', 'ground_truth', 'mzML')   
    csv_file = os.path.join(results_dir, 'extracted_peaks_ms1.csv')
    P_peaks_df = get_df(csv_file, min_ms1_intensity, rt_range, mz_range)

    csv_file = os.path.join(experiment_out_dir, 'extracted_peaks_ms1.csv')
    Q_peaks_df = get_df(csv_file, min_ms1_intensity, rt_range, mz_range)

    fullscan_filename = 'Beer_multibeers_1_fullscan1.mzML'   
    matching_mz_tol = 10 # ppm
    matching_rt_tol = 30 # seconds

    results = []
    for N in Ns:
        for rt_tol in rt_tols:

            # load chemicals and check for matching
            chemicals = load_obj(os.path.join(experiment_out_dir, 'dataset.p'))           
            fragfile_filename = 'experiment_%s_N_%d_rttol_%d.mzML' % (experiment_name, N, rt_tol) 

            # load controller and compute performance
            controller = load_controller(experiment_out_dir, experiment_name, N, rt_tol)
            mytemp = os.path.join(url_experiment_out_dir, fragfile_filename)
            pathlist.append(mytemp)
            
            if controller is not None:
                tp, fp, fn, prec, rec, f1 = compute_performance_scenario_2(controller, chemicals, min_ms1_intensity,
                                                                           fullscan_filename, fragfile_filename,
                                                                           P_peaks_df, Q_peaks_df, matching_mz_tol, matching_rt_tol)
                print('%s N=%d rt_tol=%d tp=%d fp=%d fn=%d prec=%.3f rec=%.3f f1=%.3f' % (experiment_name, 
                    N, rt_tol, tp, fp, fn, prec, rec, f1))
                res = (experiment_name, N, rt_tol, tp, fp, fn, prec, rec, f1)    
                results.append(res)  
    result_df = pd.DataFrame(results, columns=['experiment', 'N', 'rt_tol', 'TP', 'FP', 'FN', 'Prec', 'Rec', 'F1'])

    plt.figure(figsize=(12, 6))
    ax = sns.lineplot(x='N', y='Prec', hue='experiment', legend='brief', data=result_df)
    plt.title('Top-N Precision')
    for l in ax.lines:
        plt.setp(l, linewidth=5)
    plt.ylabel('Precision')
    plt.xlabel(r'Top-$N$')
    plt.legend(prop={'size': 20})
    plt.tight_layout()

    fig_out = os.path.join(experiment_out_dir, 'topN_precision.png')
    plt.savefig(fig_out, dpi=300)

    plt.figure(figsize=(12, 6))
    ax = sns.lineplot(x='N', y='Rec', hue='experiment', legend='brief', data=result_df)
    plt.title('Top-N Recall')
    for l in ax.lines:
        plt.setp(l, linewidth=5)
    plt.ylabel('Recall')
    plt.xlabel(r'Top-$N$')
    plt.legend(prop={'size': 20})
    plt.tight_layout()

    fig_out = os.path.join(experiment_out_dir, 'topN_recall.png')


    plt.figure(figsize=(12, 6))
    ax = sns.lineplot(x='N', y='F1', hue='experiment', legend='brief', data=result_df)
    plt.title('Top-N F1')
    for l in ax.lines:
        plt.setp(l, linewidth=5)
    plt.ylabel(r'$F_{1}\;score$')
    plt.xlabel(r'Top-$N$')
    plt.legend(prop={'size': 20})
    plt.tight_layout()

    fig_out = os.path.join(experiment_out_dir, 'topN_f1.png')
    plt.savefig(fig_out, dpi=300)

    return pathlist