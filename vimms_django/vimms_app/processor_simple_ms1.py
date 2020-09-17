import sys
sys.path.append('../..')
from pathlib import Path

from vimms.Chemicals import ChemicalCreator
from vimms.MassSpec import IndependentMassSpectrometer
from vimms.Controller import SimpleMs1Controller
from vimms.Environment import Environment
from vimms.Common import *


def simple_ms1_processor():
    print('#'*10, 'Load previously trained spectral feature database and the list of extracted metabolites, \
        created in 01. Download Data')
    #-----------------
    mypath = 'documents/simple_ms1/example_data'
    #-----------------
    base_dir = os.path.abspath(mypath)
    ps = load_obj(Path(base_dir, 'peak_sampler_mz_rt_int_19_beers_fullscan.p'))
    hmdb = load_obj(Path(base_dir, 'hmdb_compounds.p'))

    # set_log_level_debug()
    out_dir = Path(base_dir, 'results', 'MS1_single')
    # the list of ROI sources created in the previous notebook '01. Download Data.ipynb'
    ROI_Sources = [str(Path(base_dir,'DsDA', 'DsDA_Beer', 'beer_t10_simulator_files'))]

    # minimum MS1 intensity of chemicals
    min_ms1_intensity = 1.75E5

    # m/z and RT range of chemicals
    rt_range = [(0, 1440)]
    mz_range = [(0, 1050)]

    # the number of chemicals in the sample
    n_chems = 6500

    # maximum MS level (we do not generate fragmentation peaks when this value is 1)
    ms_level = 1

    chems = ChemicalCreator(ps, ROI_Sources, hmdb)
    dataset = chems.sample(mz_range, rt_range, min_ms1_intensity, n_chems, ms_level)
    save_obj(dataset, Path(out_dir, 'dataset.p'))

    for chem in dataset[0:10]:
        print(chem)
    print('#'*10, 'Run MS1 controller on the samples and generate .mzML files')
    min_rt = rt_range[0][0]
    max_rt = rt_range[0][1]

    mass_spec = IndependentMassSpectrometer(POSITIVE, dataset, ps)
    controller = SimpleMs1Controller()

    # create an environment to run both the mass spec and controller
    env = Environment(mass_spec, controller, min_rt, max_rt, progress_bar=True)

    # set the log level to WARNING so we don't see too many messages when environment is running
    set_log_level_warning()

    # run the simulation
    env.run()
    set_log_level_debug()
    mzml_filename = 'ms1_controller.mzML'
    env.write_mzML(out_dir, mzml_filename)
    return str(Path(mypath, 'results', 'MS1_single')) + '/' + mzml_filename