from flask import Flask, render_template, request, send_from_directory, jsonify
import os
from flask_httpauth import HTTPBasicAuth
import db_utils
import multiprocessing
import worker


app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['UPLOAD_FOLDER'] = "attachments/"


@auth.verify_password
def verify_pw(username, password):
    sess = db_utils.get_session()
    r_user = sess.query(db_utils.Config.config_value).filter_by(config_key="admin_user").first()[0]
    r_pass = sess.query(db_utils.Config.config_value).filter_by(config_key="admin_password").first()[0]
    if (username == r_user) and (password == r_pass):
        return True
    else:
        return False


@app.route('/')
@auth.login_required
def hello_world():
    return render_template("index.html")


@app.route('/api/get_tasks', methods=["GET"])
@auth.login_required
def get_tasks():
    sess = db_utils.get_session()
    tasks = sess.query(db_utils.Task).with_entities(db_utils.Task.id, db_utils.Task.task_show_name, db_utils.Task.task_from_address, db_utils.Task.task_to_address, db_utils.Task.task_status, db_utils.Task.task_msg)
    ret = [dict(zip(["id", "task_show_name", "task_from_address", "task_to_address", "task_status", "task_msg"], task)) for task in tasks]
    sess.close()
    return jsonify(ret)


@app.route('/api/start_sending', methods=["GET"])
@auth.login_required
def start_sending():
    process = multiprocessing.Process(target=worker.run)
    process.start()
    return str(process.pid)


@app.route('/upload', methods=["POST"])
@auth.login_required
def upload():
    ret = list()
    for file in request.files:
        request.files[file].save(os.path.join(app.config['UPLOAD_FOLDER'], request.files[file].filename))
        ret.append(request.files[file].filename)
    return jsonify(ret)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/parse_list', methods=["POST"])
@auth.login_required
def parse_list():
    ret = list()
    for file in request.files:
        ret.extend([item for item in request.files[file].stream.read().decode("UTF-8").replace("\ufeff", "").split()])
    return jsonify(ret)


@app.route("/api/submit", methods=["POST"])
@auth.login_required
def submit():
    sess = db_utils.get_session()
    for to_addr in request.form.get("task_to_address").split("|"):
        sess.add(db_utils.Task(task_show_name=request.form.get("task_show_name"),
                               task_from_address=request.form.get("task_from_address"),
                               task_to_address=to_addr,
                               task_subject=request.form.get("task_subject"),
                               task_body=request.form.get("task_body"),
                               task_atts=request.form.get("task_atts"),
                               task_status="Queued",
                               task_msg=""))
    sess.commit()
    sess.close()
    return "1"


@app.route("/api/clear_done", methods=["GET"])
@auth.login_required
def clear_done():
    sess = db_utils.get_session()
    sess.query(db_utils.Task).filter_by(task_status="Done").delete()
    sess.commit()
    sess.close()
    return "1"


@app.route("/api/requeue", methods=["GET"])
@auth.login_required
def requeue():
    sess = db_utils.get_session()
    sess.query(db_utils.Task).filter_by(task_status="Failed").update({"task_status": "Queued", "task_msg": ""})
    sess.commit()
    sess.close()
    return "1"


@app.route("/api/get_atts", methods=["GET"])
@auth.login_required
def get_atts():
    return jsonify(os.listdir("attachments/"))


@app.route("/api/del_att/<filename>", methods=["GET"])
@auth.login_required
def del_att(filename):
    os.remove("attachments/{}".format(filename))
    return "1"


@app.route("/api/clear_all", methods=["GET"])
@auth.login_required
def clear_all():
    sess = db_utils.get_session()
    sess.query(db_utils.Task).delete()
    sess.commit()
    sess.close()
    return "1"


if __name__ == '__main__':
    app.run(debug=True)
