from fastapi import FastAPI
from c2x import clean_cif_c2x, clean_cif_content_c2x
from models import InputFile

app = FastAPI()


@app.post("/api/v1/clean-cif/")
def api_v1_clean(inputfile:InputFile):
    result, cif, cif_string = clean_cif_content_c2x(inputfile.fileContent)
    print(result)
    return {'clean': True,
            'cif_string': cif_string}

@app.post("/api/v1/clean-cif-dev/")
def api_v1_clean_dev():
    result, cif , cif_string = clean_cif_c2x('HKUST1_exp.cif')
    print(result)
    return {'clean': True,
            'cif_string': cif_string}

@app.post("/api/v1/cleaning/") 
def api_v1_test():
    print('From cleaning app: check')
    return {'test': True}


