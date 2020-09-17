import sys
sys.path.append('../..')

from pathlib import Path

from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Controller import TreeController
from vimms.Environment import Environment
from vimms.Common import *


def dia_processor():
    # data_dir = os.path.abspath(os.path.join(os.getcwd(),'..','..','tests','integration','fixtures'))
    # print(data_dir)
    mypath = 'documents/prepared_data_dia'
    data_dir = os.path.join(os.getcwd(), mypath)

    dataset = load_obj(os.path.join(data_dir, 'QCB_22May19_1.p'))
    ps = load_obj(Path(data_dir,'peak_sampler_mz_rt_int_beerqcb_fragmentation.p'))

    rt_range = [(0, 1440)]
    min_rt = rt_range[0][0]
    max_rt = rt_range[0][1]

    dia_design = 'basic'
    window_type = 'even'
    kaufmann_design = None
    extra_bins = 0
    num_windows = 1

    mass_spec = IndependentMassSpectrometer(POSITIVE, dataset, ps)
    controller = TreeController(dia_design, window_type, kaufmann_design, extra_bins, num_windows)

    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    print('#'*10, 'run the simulation')
    env.run()

    print('#'*10, 'Run Fixed Window DIA')
    rt_range = [(0, 1440)]
    min_rt = rt_range[0][0]
    max_rt = rt_range[0][1]

    dia_design = 'basic'
    window_type = 'even'
    kaufmann_design = None
    extra_bins = 0
    num_windows = 10

    mass_spec = IndependentMassSpectrometer(POSITIVE, dataset, ps)
    controller = TreeController(dia_design, window_type, kaufmann_design, extra_bins, num_windows)

    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    # run the simulation
    env.run()

    print('#'*10, 'Run Tree DIA method of Kauffman and Walker')
    rt_range = [(0, 1440)]
    min_rt = rt_range[0][0]
    max_rt = rt_range[0][1]

    dia_design = 'kaufmann'
    window_type = 'even'
    kaufmann_design = 'tree'
    extra_bins = 0
    num_windows=10

    mass_spec = IndependentMassSpectrometer(POSITIVE, dataset, ps)
    controller = TreeController(dia_design, window_type, kaufmann_design, extra_bins, num_windows)
    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    # run the simulation
    env.run()
    print('#'*10, 'Run Nested DIA method of Kauffman and Walker')
    rt_range = [(0, 1440)]
    min_rt = rt_range[0][0]
    max_rt = rt_range[0][1]

    dia_design = 'kaufmann'
    window_type = 'even'
    kaufmann_design = 'nested'
    extra_bins = 0

    mass_spec = IndependentMassSpectrometer(POSITIVE, dataset, ps)
    controller = TreeController(dia_design, window_type, kaufmann_design, extra_bins, num_windows)
    num_windows=10
    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    # run the simulation
    env.run()
    mzml_filename = 'dia_controller.mzML'
    out_dir = os.path.join(data_dir, 'results')
    env.write_mzML(out_dir, mzml_filename)
    return str(Path(mypath, 'results')) + '/' + mzml_filename