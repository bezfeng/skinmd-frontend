from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
from werkzeug.contrib.fixers import ProxyFix
from twss import TWSSObj
import os, errno, time

app = Flask(__name__)
twssObj = TWSSObj()

# website static content
@app.route('/')
@app.route('/index.html')
def show_index():
	return render_template('index.html');

@app.route('/team.html')
def show_team():
	print "Rendering team page"
	return render_template('team.html');
	
@app.route('/support.html')
def show_support():
	print "Rendering support page"
	return render_template('support.html');

# mobile results
@app.route('/mobile/results/<id>')
def show_mobile_result(id):
	diagnosis = find_data(id)
	print "mobile diagnosis: %s " % diagnosis
	rv = app.make_response(diagnosis)
	rv.mimetype = 'text/plain'
	return rv
	
	#filename = 'get.png'
	#return send_file(filename, mimetype = 'image/png')

@app.route('/view/<id>')
def show_view(id):
	filename = 'processed/' + id;
	return send_file(filename, mimetype = 'image/jpeg');

# web results
@app.route('/results/<id>')
def show_user_result(id):
	diagnosis = find_data(id)
	if diagnosis == -1:
		diagnosis = "Sorry, we can't find the result for this ID"

	return render_template('results.html', id = id, res = diagnosis)

@app.route('/results-all/')
def show_all_results():
	result_dict = {}
	print "Displaying all results"
	
	try:
		f = open('data.txt', 'r')
		for line in f:
			line_split = line.strip().split(',')
			result_dict[line_split[0]] = [line_split[1], line_split[2]]
			
			print result_dict[line_split[0]]
		
		f.close()
	except:
		result_dict['No'] = ['Results', 'Now'];
	return render_template('all.html', result_dict = result_dict)
		
def find_data(id):
	print "Finding data for %s" % id
	result = "-1"
	try:
		f = open('data.txt', 'r')
		
		for line in f:
			line_split = line.strip().split(',')
			if line_split[0] == id:
				result = line_split[2]
		f.close()
		return result
	except:
		return "error finding file"
	

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		print "Received post!"
		try:
			for id in request.files:
				f = request.files[id]
				# create images directory if not present
				try:
					os.makedirs('images')
				except OSError, e:
					if e.errno != errno.EEXIST:
						raise
				if f:
					f.save('images/' + secure_filename(f.filename))
					print "%s saved!" % f.filename
					return "%s saved!" % f.filename
		except:
			print "error saving file"

@app.route('/twss/<quote>')
def process_twss(quote):
	return twssObj.twss_check(quote)

if __name__ == '__main__':
	#app.run(debug=True, port = 5000, host = '0.0.0.0')
	app.wsgi_app = ProxyFix(app.wsgi_app)
