from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from flask_session import Session
import openpyxl
 
app = Flask(__name__, static_url_path='/static')
# Configure Flask to use Redis for sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.secret_key = 'your_secret_key'

# In-memory storage for submitted data (now stored in the session)
def get_submitted_data():
    return session.get('submitted_data', {})

def set_submitted_data(data):
    session['submitted_data'] = data

# Load Excel data into session on app startup
def load_excel_data(): 
    excel_file = 'blackbox.xlsx'  # Provide the actual file path
    workbook = openpyxl.load_workbook(excel_file)
    
    excel_data = {}
    
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        data = {}
        for row in sheet.iter_rows(min_row=1, values_only=True):
            #print("ROW content - ",row)
            is_yes_or_no, question, value, image_paths = row   
            if is_yes_or_no == "Yes":
                if not image_paths:
                    image_path_list = ['noimage.png']
                elif ';' in image_paths:
                    image_path_list = image_paths.split(';')
                else:
                    image_path_list = [image_paths]

                value = value.replace("'", "").replace('"', '').replace(':', '-')
                data[question] = {'value': value, 'image_paths': image_path_list}
        excel_data[sheet_name] = data
    #print("total data>>>>>>:", excel_data)
    return excel_data

# Load Excel data at app startup (just once)
excel_data = load_excel_data()
 
@app.route('/')
def index(): 
    submitted_data = get_submitted_data()
    return render_template('candidate.html', submitted_data=submitted_data)

@app.route('/candidate')
def candidate():  
    submitted_data = get_submitted_data()
    return render_template('candidate.html', submitted_data=submitted_data)

@app.route('/admin', methods=['GET', 'POST'])
def admin(): 
    if request.method == 'POST':
        
        print("Received data  >>>>>>  :", request.get_data())
 
        data = request.get_json()
        sheetname = data['sheetname']
        question = data['question']

        if sheetname in excel_data and question in excel_data[sheetname]:
            entry_data = excel_data[sheetname][question]
            answer = entry_data['value']
            image_paths = entry_data['image_paths']
            
        else:
            answer = None
            image_paths = None
      
        response_data = {'answer': answer, 'image_paths': image_paths}
        submitted_data = get_submitted_data()
        submitted_data.clear()
        submitted_data[question] = response_data
        set_submitted_data(submitted_data)

        with open('values.txt', 'w') as file:
            file.write(f'Sheet Name: {sheetname}, Question: {question}\n')

    return render_template('admin.html', excel_data=excel_data);

@app.route('/check_update')
def check_update(): 
    current_data_hash = hash(str(get_submitted_data()))
    print(current_data_hash)
    print(session.get('current_data_hash', None))
    if current_data_hash != session.get('current_data_hash', None):
        session['current_data_hash'] = current_data_hash
        return jsonify({'updated': True})
    
    return jsonify({'updated': False})

if __name__ == '__main__':
    app.run(debug=True)
