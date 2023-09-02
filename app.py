from flask import Flask, render_template, request, redirect, url_for, session
import openpyxl
 
app = Flask(__name__, static_url_path='/static')
 
# Set a secret key for session management
app.secret_key = 'your_secret_key'

# Load Excel data into session on app startup
def load_excel_data():
    print("    am inside load_Excel_Data!!!!!   ")
    excel_file = 'blackbox.xlsx'  # Provide the actual file path
    workbook = openpyxl.load_workbook(excel_file)
    
    excel_data = {}
    
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        data = {}
        for row in sheet.iter_rows(min_row=1, values_only=True):
            key, value, image_paths = row  # Assuming image paths are in column 3
            image_path_list = image_paths.split(';')  # Split paths using a delimiter
            data[key] = {'value': value, 'image_paths': image_path_list}
        excel_data[sheet_name] = data
        
    print(">>>>>>>>>>>>>>>>",excel_data)
    return excel_data

# In-memory storage for submitted data.
submitted_data = {}

 
@app.route('/')
def index():
    session['excel_data'] = load_excel_data()
    return redirect(url_for('candidate'))

@app.route('/reset')
def reset():
    submitted_data = {}
    return redirect(url_for('admin'))

@app.route('/admin', methods=['GET', 'POST'])
def admin(): 
    if request.method == 'POST':
        
        print("Received data>>>>>>:", request.get_data())
 
        data = request.get_json()
        sheetname = data['sheetname']
        question = data['question']
        
        # Retrieve Excel data from session
        excel_data = session['excel_data']
        
        # Using the variable 'question' as row_key was not defined. Let's fix that.
        row_key = question
        
        if row_key in excel_data.get(sheetname, {}):
            entry_data = excel_data[sheetname][row_key]
            answer = entry_data['value']
            image_paths = entry_data['image_paths']
        else:
            answer = None
            image_paths = None
        
        # Store the data in the dictionary using the question as the key
        submitted_data[question] = {'answer': answer, 'image_paths': image_paths}
    
    return render_template('admin.html')

@app.route('/candidate')
def candidate(): 
    print(">>>>....submitted_data........>>>>>>",submitted_data)
    return render_template('candidate.html', submitted_data=submitted_data)

if __name__ == '__main__':
    app.run(debug=True)
