from pydantic import BaseModel, Field
from typing import Optional

class UploadedData(BaseModel):
    """File to predict"""

    data:dict = Field(description= 'Content of Input File')
    extension: Optional[str] = 'json'
