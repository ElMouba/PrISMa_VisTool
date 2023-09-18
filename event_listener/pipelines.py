import requests
from config_pdf import *

def cleaning(cif_content):

    data = {'fileContent' : cif_content}
    url = "http://cleaning:8083/api/v1/clean-cif/"

    clean_cif = requests.post(url, json = data).json()

    return clean_cif['cif_string']

def adsorbaphore_models(cif_content_clean):
    url = "http://models:8084/api/v1/all-models/"
    data = {'fileContent' : cif_content_clean}

    predictions = requests.post(url, json = data).json()
    return predictions

def send_email(form, model_outputs_data):
    print('From send_email: start')
    
    url = "http://email:8085/sendresults/"

    results = {'submissionform': form,
            'predictions':model_outputs_data}
    
    data2 = DATA

    print('Data: ', results)
    print('Data2: ', data2)
    print('sending...')
    print(model_outputs_data)
    test = requests.post("http://email:8085/test/") 
    print(test.text)
    final = requests.post(url, json = results)
    print(final.text, flush=True)
    final = final.json()
    return final   
   
def pipe(form):
    if DUMMY:
        print('DUMMY!')
        model_outputs_data = DUMMY_MODEL_OUTPUT
        data = DUMMY_FORM
        send_email(data, model_outputs_data)
        return True

    print('Start in Pipe OK; START Clean', flush = True)
    clean_cif = cleaning(form['CifContent'])

    print('Clean OK; START models', flush=True)
    preds = adsorbaphore_models(clean_cif)

    print('models OK; START email', flush=True)
    send_email(form, preds)
    return True
