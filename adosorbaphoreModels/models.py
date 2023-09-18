from pydantic import BaseModel, Field
from typing import Optional, Dict, List

class InputFile(BaseModel):
    """File to predict"""

    fileContent:str = Field(description= 'Content of Input File')
    extension: Optional[str] = 'cif'

class ModelResult(BaseModel):
    """Output of ML model"""
    model_name: str
    model_input_type: str
    model_input_value: Dict
    prediction: int
    prediction_explanation: str = 'No explanation provided'


class AllModelResult(BaseModel):
    model_outputs: Dict[str, ModelResult]