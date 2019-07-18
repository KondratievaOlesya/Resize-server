import os
import uuid
from flask import render_template, request, redirect, flash, abort
from app import app, db, celery
from app.models import ImageRequest, READY, NOT_READY
from PIL import Image
from app.forms import ImageForm

ALLOWED_EXTENSIONS = (['png', 'jpg'])
UPLOAD_FOLDER = os.path.join('app', 'static')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@celery.task(bind=True)
def change_img_size(self, filename, w, h, Id):
    img = Image.open(os.path.join(UPLOAD_FOLDER, filename))
    new_img = img.resize((w, h))
    new_img.save(fp=os.path.join(UPLOAD_FOLDER, filename))

    db.session.query(ImageRequest). \
        filter_by(id=Id). \
        update({'status': READY})
    db.session.commit()
    return {'status': 'Task completed!'}


@app.route('/', methods=['POST', 'GET'])
def index():
    form = ImageForm()
    if form.validate_on_submit():
        w = form.w.data
        h = form.h.data
        file = form.img.data
        if allowed_file(file.filename):
            file_extension =os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + file_extension
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            flash('File successfully uploaded')
            new_record = ImageRequest(w=w, h=h, img_path=filename)
            db.session.add(new_record)
            db.session.commit()
            change_img_size.apply_async(args=[filename, w, h, new_record.id])
            flash('Your task id is ' + str(new_record.id))
            return render_template('index.html', form=form), 202
        else:
            flash('Allowed file types are png, jpg')
            return redirect(request.url), 301

    return render_template('index.html', form=form), 200


@app.route('/status/<task_id>')
def task_status(task_id):
    if db.session.query(ImageRequest).filter_by(id=task_id).first():
        ImageRequestRecord = ImageRequest.query.get(task_id)
        return render_template('status.html', ImageRequest=ImageRequestRecord), 200
    else:
        abort(404)
