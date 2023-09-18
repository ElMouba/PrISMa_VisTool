from pdf import OverviewPDF
from submission_form import SubmissionForm


model_output = {'model_outputs': [{'model_name': 'nCAC',
   'model_input_type': 'PHImage',
   'prediction': 0,
   'prediction_explanation': 'whether a material has a lower nCAC than the MEA-based benchmark'},
  {'model_name': 'WaterResistance',
   'model_input_type': 'PHImage',
   'prediction': 1,
   'prediction_explanation': 'whether a material can maintain its CO2 adsorption capacity in wet flue gasses'}]}

data = {
    "FirstName": "Joren",
    "LastName": "Van Herck",
    "Email": "vanherck.joren@gmail.com",
    "Affiliation": "EPFL",
    "Position": "PostDoc",
    "StructureName": "TEST",
    "StructureDOI": "unknown",
    "Type": "Experimental",
    "Remarks": "This is a final test",
    "Consent": "I Agree",
    "CifName": "HKUST1_exp.cif",
    "CifBaseName": "HKUST1_exp",
    "SubmissionTime": "2023-08-10 09:37"
}
subform = SubmissionForm(data)
table = subform.get_table()

pdf = OverviewPDF(submission_form = table, models_output=model_output)

pdf.save_pdf()

print(pdf.get_pdfbytes())