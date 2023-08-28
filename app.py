from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory storage for submitted data
submitted_data = []

@app.route('/')
def index():
    return redirect(url_for('candidate'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = request.form['data']
        submitted_data = [data]
    return render_template('admin.html')

@app.route('/candidate')
def candidate():
    return render_template('candidate.html', submitted_data=submitted_data)

if __name__ == '__main__':
    app.run(debug=True)
