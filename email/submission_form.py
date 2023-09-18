STANDARD_KEYS = {'FullName': 'Name',
 'Affiliation': 'Affiliation',
 'Position': 'Position',
 'SubmissionTime': 'Submission time',
 'StructureName': 'Structure Name',
 'CifName': 'Submitted cif',
 'Remarks':'Remarks'}

class SubmissionForm():
    def __init__(self, form:dict) -> None:

        self.original_form = form
        self.form = form

        self.first_name:str = form['FirstName']
        self.last_name:str = form['LastName']
        self._add_fullname()

        self.keys = list(form.keys())

    
    def _add_fullname(self):
        self.form['FullName'] = self.first_name + ' ' +self.last_name

    def get_form(self, allowed_keys:list = None):
        if allowed_keys == None:
            allowed_keys = self.keys

        return {key: self.form[key] for key in self.form if key in allowed_keys}

    def get_table(self):
        return {STANDARD_KEYS[key]:self.form[key] for key in STANDARD_KEYS.keys() if key in self.form.keys()}
