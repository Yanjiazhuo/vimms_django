# vimms_django


************** attention please **************

1.  To be able to upload and process the example_data.zip compressed package, you need hmdb_compounds.p file
    

     Change hmdb_compounds.p from hmdb_metabolites.xml (an xml that exceeds 4G in size)
     It takes 3-4 hours to decompress and process, which is too long.
     To process hmdb_compounds.p from the compressed package, you need to do the following:
    3.1 Configuration location: modify line 24 in pre_proces.py in the project =>
   url = '/Users/abel/Downloads/hmdb_metabolites.xml' The location of hmdb_metabolites.xml in the local file，
   hmdb_metabolites.xml from hmdb_metabolites.zip. According to the vimms document, you need to extract from:
   http://www.hmdb.ca/system/downloads/current/hmdb_metabolites.zip Download the zip package。

     The relevant code of the vimms package author needs to be improved so that the code can handle huge xml files:
    example：/usr/local/lib/python3.7/site-packages/vimms-1.1.0-py3.7.egg/vimms/DataGenerator.py
    DataGenerator.py  need to speedup function: extract_hmdb_metabolite
    from line 19, extract_hmdb_metabolite function change into:

def extract_hmdb_metabolite(in_file, delete=True):
    logger.debug('Extracting HMDB metabolites from %s' % in_file)

    count = 0
    # loops through file and extract the necessary element text to create a DatabaseCompound
    db = xml.etree.ElementTree.parse(f).getroot()
    logger.debug('##')
    compounds = []
    prefix = '{http://www.hmdb.ca}'
    for metabolite_element in db:
        count += 1
        if count % 1000 == 0:
            logger.debug('count=%s' % count)
        row = [None, None, None, None, None, None]
        for element in metabolite_element:
            if element.tag == (prefix + 'name'):
                row[0] = element.text
            elif element.tag == (prefix + 'chemical_formula'):
                row[1] = element.text
            elif element.tag == (prefix + 'monisotopic_molecular_weight'):
                row[2] = element.text
            elif element.tag == (prefix + 'smiles'):
                row[3] = element.text
            elif element.tag == (prefix + 'inchi'):
                row[4] = element.text
            elif element.tag == (prefix + 'inchikey'):
                row[5] = element.text

        # if all fields are present, then add them as a DatabaseCompound
        if None not in row:
            compound = DatabaseCompound(row[0], row[1], row[2], row[3], row[4], row[5])
            compounds.append(compound)
    logger.info('Loaded %d DatabaseCompounds from %s' % (len(compounds), in_file))

    # f.close()
    # if zf is not None:
    #     zf.close()

    if delete:
        logger.info('Deleting %s' % in_file)
        os.remove(in_file)

    return compounds



1. If need to run vary n in topn later, note that you need to configure the R environment to run the R script of the relevant vimms package.
The R script package is in extract_peaks.R in example_data/results/beer1pos
Run: RScript extract_peaks.R
You need to install all the dependencies of the R library required to run extract_peaks.R in advance, and you need to install the dependencies using BiocManager.
Execute in the interpreter:
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("xcms")


1. To execute the test, you need to go to the directory with manager.py (the relative project directory is under vimms_django/vimms_django),
Then execute in the bash command line：python3 manage.py test
If the normal feedback is:

Destroying test database for alias 'default'...
(samaritan1)abeltekiMacBook-Pro:vimms_django abel$ python3 manage.py test
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.
----------------------------------------------------------------------
Ran 1 test in 0.004s

OK

If the error feedback is:
ERROR: test_model_use (vimms_app.tests.DocumentModelTestCase)
Document upload/download are correctly identified

----------------------------------------------------------------------
Ran 1 test in 0.010s

FAILED (errors=1)
Destroying test database for alias 'default'...
