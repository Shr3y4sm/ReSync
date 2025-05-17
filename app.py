from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from io import BytesIO


class Base(DeclarativeBase):
  pass


app = Flask(__name__)

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///docs.db"
db.init_app(app)


class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    semester = db.Column(db.String(250), nullable=False)
    branch = db.Column(db.String(250), nullable=False)
    subject = db.Column(db.String(250), nullable=False)
    filename = db.Column(db.String(250), nullable=False)
    filedata = db.Column(db.LargeBinary)


with app.app_context():
    db.create_all()


@app.route('/', methods=["GET", "POST"])
def home():
    result = db.session.execute(db.select(Doc).order_by(Doc.id))
    all_docs = result.scalars().all()
    return render_template("index.html", books=all_docs)


@app.route("/delete")
def delete():
    doc_id = request.args.get('id')
    doc_to_delete = db.get_or_404(Doc, doc_id)
    db.session.delete(doc_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        doc_id = request.form["id"]
        doc_to_update = db.get_or_404(Doc, doc_id)
        doc_to_update.title = request.form["title"]
        doc_to_update.semester = request.form["semester"]
        doc_to_update.branch = request.form["branch"]
        doc_to_update.subject = request.form["subject"]
        doc_to_update.filename = request.files["file"].filename
        doc_to_update.filedata = request.files["file"].read()
        db.session.commit()
        return redirect(url_for('home'))
    doc_id = request.args.get('id')
    doc_selected = db.get_or_404(Doc, doc_id)
    return render_template("edit.html", book=doc_selected)


@app.route('/download/<upload_id>')
def download(upload_id):
    upload = Doc.query.filter_by(id=upload_id).first()
    return send_file(BytesIO(upload.filedata), download_name=upload.filename, as_attachment=True)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_doc = Doc(
            title=request.form["title"],
            semester=request.form["sem"],
            branch=request.form["branch"],
            subject=request.form["subject"],
            filename=request.files['file'].filename,
            filedata=request.files['file'].read()
        )
        db.session.add(new_doc)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", books=Doc)


if __name__ == "__main__":
    app.run(debug=True)
