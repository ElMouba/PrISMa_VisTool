import os
import shutil
from pathlib import Path
import subprocess
from ase.io.cif import write_cif

def clean_cif_c2x(infile:str, outfile = None, in_extension = '.cif'):
    '''
    Extracts primitive cell from cif file by running C2X -P --pya (find primitive cell with own internal algorithm, not spglib. as a python ASE Atoms data structure.)
    
    docs of c2x : http://www.c2x.org.uk/downloads/c2x_man.html

    Parameters:
    -----------
    infile: str
        cif file that needs to be cleaned
    outfile: None, str (default: None)
        name of cleaned cif file. Include .cif extension

    Returns:
    ---------    
    atoms: ase.atoms.Atoms
                
    outfile:str
        directory of clean cif file
    '''

    if infile.endswith('.cif'):
        stem = infile.split('.cif')[0]
    else:
        stem = infile
        infile = infile + in_extension

    if outfile == None:
        outfile = f'{stem}_clean.cif'
        
    tempfile = f'{stem}_temp.py'

    subprocess.run(["./c2x_linux", 
                    '-P', 
                    '--pya', 
                    infile, 
                    tempfile])

    with open(tempfile, "r") as handle:
        code_to_execute = handle.read()

    my_context = {"structure": None}
    exec(code_to_execute, globals(), my_context)

    atoms = my_context["structure"]
    if atoms == None:
        raise ValueError('C2X failed in recreating a clean structure')
        
    write_cif(outfile, atoms)

    with open(outfile , '+r') as f:
        cif_string = f.read()
        
    os.remove(tempfile)
    os.remove(outfile)

    return atoms, outfile, cif_string    
    

def clean_cif_content_c2x(cif_content:str, outfile = None, in_extension = '.cif'):
    '''
    Extracts primitive cell from cif file by running C2X -P --pya (find primitive cell with own internal algorithm, not spglib. as a python ASE Atoms data structure.)
    
    docs of c2x : http://www.c2x.org.uk/downloads/c2x_man.html

    Parameters:
    -----------
    infile: str
        cif file that needs to be cleaned
    outfile: None, str (default: None)
        name of cleaned cif file. Include .cif extension

    Returns:
    ---------    
    atoms: ase.atoms.Atoms
                
    outfile:str
        directory of clean cif file
    '''
    stem = 'uploaded_ciffile'

    temp_cif = f'{stem}_cif.cif'
    with open(temp_cif, 'w+') as f:
        f.write(cif_content)

    if outfile == None:
        outfile = f'{stem}_clean.cif'
        
    tempfile = f'{stem}_temp.py'


    subprocess.run(["./c2x_linux", 
                    '-P', 
                    '--pya', 
                    temp_cif, 
                    tempfile])

    with open(tempfile, "r") as handle:
        code_to_execute = handle.read()

    my_context = {"structure": None}
    exec(code_to_execute, globals(), my_context)

    atoms = my_context["structure"]
    if atoms == None:
        raise ValueError('C2X failed in recreating a clean structure')
        
    write_cif(outfile, atoms)

    with open(outfile , '+r') as f:
        cif_string = f.read()
        
    os.remove(tempfile)
    os.remove(outfile)

    return atoms, outfile, cif_string    
    