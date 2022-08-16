import base64
import secrets

from flask import Flask, request, flash, render_template, redirect

from app.connection import Computation
from app.log import get_logger

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe()


log = get_logger("SERVER")


ACTIVE_COMPUTATIONS = dict()


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file parts", "error")
        file = request.files['file']
        if file.filename == '':
            flash('No selected files', "error")
            return redirect(request.url)

        file_bytes = file.stream.read()

        try:
            computation = Computation(image_bytes=file_bytes)
            ACTIVE_COMPUTATIONS[computation.image_id] = computation
            computation.spawn_listener()
            computation.send()
            return redirect(f"/{computation.image_id}")
        except Exception as e:
            log.error("Unexpected error.", exc_info=e)
            flash(str(e), "error")

    return render_template("home.html", computations=ACTIVE_COMPUTATIONS.values())


@app.route("/<computation_id>", methods=["GET"])
def status(computation_id):
    if computation_id not in ACTIVE_COMPUTATIONS:
        return "", 404

    computation = ACTIVE_COMPUTATIONS[computation_id]
    image_as_b64 = base64.b64encode(computation.image_bytes)
    return render_template(
        "status.html",
        computation=computation,
        image_bytes=image_as_b64.decode()
    )
