from flask import Flask, render_template, send_from_directory, request, redirect, flash, url_for

import cor

app = Flask(__name__, static_folder='static')
### COMMON ###
@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/run', methods=['POST'])
def run():
    error = None
    if request.method == 'POST':
		result = cor.run(str(request.form["in"]))
		return result
    error = 'An error has occurred.'
    return 'ERROR: %s' % error

@app.route('/<path:path>')
def send_img(path):
    return send_from_directory('static', path)
    
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
