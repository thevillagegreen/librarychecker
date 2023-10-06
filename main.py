from flask import Flask, render_template, request, url_for, flash, redirect
import urllib.parse
import checker

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def index():
  if request.method == 'POST':
    library_path = urllib.parse.quote(request.form['library_path'], safe="")

    if not library_path:
      flash('library path is required')
    else:
      return redirect(url_for('results', library_path=library_path))
    
  return render_template('index.html')

@app.route('/results/<library_path>/')
def results(library_path):
  library_path = urllib.parse.unquote(library_path)
  results_obj = checker.run(library_path)
  return render_template('results.html', library_path=library_path, results_obj=results_obj)