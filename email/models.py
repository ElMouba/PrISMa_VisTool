from pydantic import BaseModel, Field
from typing import Optional, Dict

class ModelResult(BaseModel):
    """Output of ML model"""
    model_name: str
    model_input_type: str
    model_input_value: Dict
    prediction: int
    prediction_explanation: str = 'No explanation provided'

class results(BaseModel):
    """File to predict"""

    submissionform:Dict = Field(description= 'Submission form from front end')
    predictions:Dict[str, Dict] = Field(description= 'Predictions from platform')

