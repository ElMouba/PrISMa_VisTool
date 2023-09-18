OVERVIEW_TABLE_KEYS = ["FirstName", "LastName", "Email", "Affiliation", "Position", "StructureName", " StructureDOI", "Type", "Remarks", "CifName", "SubmissionTime"]

DUMMY = True

DUMMY_MODEL_OUTPUT = {
    "model_outputs": {
    "a": 
    {"model_name": "nCAC_dummy",
   "model_input_type": "PHImage",
   "prediction": 0,
   "prediction_explanation": "whether a material has a lower nCAC than the MEA-based benchmark"},
   "b":
  {"model_name": "WaterResistance_dummy",
   "model_input_type": "PHImage",
   "prediction": 1,
   "prediction_explanation": "whether a material can maintain its CO2 adsorption capacity in wet flue gasses"}
   }
}

DUMMY_FORM:dict = {
    "FirstName": "Joren",
    "LastName": "Van Herck",
    "Email": "vanherck.joren@gmail.com",
    "Affiliation": "EPFL",
    "Position": "PostDoc",
    "StructureName": "TEST",
    "StructureDOI": "unknown",
    "Type": "Experimental",
    "Remarks": "This is a DUMMY form!",
    "Consent": "I Agree",
    "CifName": "HKUST1_exp.cif",
    "CifBaseName": "HKUST1_exp",
    "SubmissionTime": "2023-08-10 09:37"
}



