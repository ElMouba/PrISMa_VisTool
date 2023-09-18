from pydantic import BaseModel, Field
from typing import Optional

class InputFile(BaseModel):
    """File to predict"""

    fileContent:str = Field(description= 'Content of Input File')
    extension: Optional[str] = 'cif'