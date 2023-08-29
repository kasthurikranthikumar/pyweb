from flask import Flask, render_template, request, redirect, url_for, session
import openpyxl

app = Flask(__name__)

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
            key, value = row
            data[key] = value
        excel_data[sheet_name] = data
        
    print(">>>>>>>>>>>>>>>>",excel_data)
    return excel_data

# In-memory storage for submitted data.
submitted_data = {}

@app.route('/')
def index():
    session['excel_data'] = load_excel_data()
    return redirect(url_for('candidate'))

@app.route('/admin', methods=['GET', 'POST'])
def admin(): 
    if request.method == 'POST':
      
        print("Received data>>>>>>:", request.get_data())
 
        data = request.get_json()
        sheetname = data['sheetname']
        question = data['question']
        print(">>>>............>>>>>>",sheetname)
        print(">>>>>,...........>>>>>>>>>>>",question)

        # Retrieve Excel data from session
        excel_data = session['excel_data']
        
        # Using the variable 'question' as row_key was not defined. Let's fix that.
        row_key = question
        
        if row_key in excel_data.get(sheetname, {}):
            answer = excel_data[sheetname][row_key]
        else:
            answer = None
        
        # Store the data in the dictionary using the question as the key
        submitted_data[question] = {'answer': answer}
    return render_template('admin.html')

@app.route('/candidate')
def candidate(): 
    print(">>>>....submitted_data........>>>>>>",submitted_data)
    return render_template('candidate.html', submitted_data=submitted_data)

if __name__ == '__main__':
    app.run(debug=True)
