from flask import Flask, render_template, request, redirect, url_for, send_from_directory # type: ignore
from moviepy.editor import VideoFileClip # type: ignore
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def video_to_gif(input_video_path, output_gif_path, start_time, end_time, resize_factor=0.5, fps=15):
    video_clip = VideoFileClip(input_video_path).subclip(start_time, end_time)
    video_clip = video_clip.resize(resize_factor)
    video_clip.write_gif(output_gif_path, fps=fps)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        start_time = float(request.form['start_time'])
        end_time = float(request.form['end_time'])
        resize_factor = float(request.form['resize_factor'])
        fps = int(request.form['fps'])
        
        output_gif_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{os.path.splitext(filename)[0]}.gif")
        video_to_gif(filepath, output_gif_path, start_time, end_time, resize_factor, fps)
        
        return redirect(url_for('uploaded_file', filename=os.path.basename(output_gif_path)))

@app.route('/output/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
