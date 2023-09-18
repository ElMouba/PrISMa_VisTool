from fastapi import FastAPI
import uvicorn
import os

from core import get_water_resistance_predictions, get_nCAC_predictions
from models import InputFile, ModelResult, AllModelResult
from config import ALLOWED_MODEL_NAMES

app = FastAPI()

@app.post("/api/v1/water-res/") 
def api_v1_predict_water_resistance(inputfile:InputFile) -> ModelResult:
    MODEL = 'WaterResistance'
    return get_water_resistance_predictions(inputfile.fileContent, inputfile.extension, model_name = MODEL)

@app.post("/api/v1/nCAC/") 
def api_v1_predict_nCAC(inputfile:InputFile) -> ModelResult:
    MODEL = 'nCAC'
    return get_nCAC_predictions(inputfile.fileContent, inputfile.extension, model_name = MODEL, dummy=False)

@app.post("/api/v1/all-models/") 
def api_v1_predict_all(inputfile:InputFile) -> AllModelResult:
    
    return AllModelResult(model_outputs={"1":get_nCAC_predictions(inputfile.fileContent, inputfile.extension, model_name = 'nCAC'),
                                         "2":get_water_resistance_predictions(inputfile.fileContent, inputfile.extension, model_name = 'WaterResistance')})

@app.post("/api/v1/test/") 
def api_v1_test():
    for root, dirs, files in os.walk("."):
        for file in files:
            print(os.path.join(root, file))
    print('From adosorbaphore app: check')
    return {'test': True}
