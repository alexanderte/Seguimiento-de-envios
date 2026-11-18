import uuid
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from database import (
    init_db,
    get_user_by_username,
    create_shipment,
    get_all_shipments,
    update_shipment_status,
    get_shipment_history,
    get_shipment_by_code
)

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import check_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("Definí la variable de entorno SECRET_KEY antes de iniciar la aplicación.")

init_db()


@app.route("/")
def inicio():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if user and check_password_hash(
            user["password_hash"], password
        ):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")




@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    envios = [dict(envio) for envio in get_all_shipments()]

    zona_argentina = ZoneInfo("America/Argentina/Buenos_Aires")

    for envio in envios:

        historial = get_shipment_history(envio["id"])
        envio["historial"] = [dict(movimiento) for movimiento in historial]

        fecha_utc = datetime.strptime(
            envio["fecha_registro"],
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        envio["fecha_registro"] = fecha_utc.astimezone(
            zona_argentina
        ).strftime("%d/%m/%Y %H:%M:%S")

        for movimiento in envio["historial"]:
            fecha_historial_utc = datetime.strptime(
                movimiento["fecha_actualizacion"],
                "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)

            movimiento["fecha_actualizacion"] = fecha_historial_utc.astimezone(
                zona_argentina
            ).strftime("%d/%m/%Y %H:%M:%S")

    return render_template(
        "dashboard.html",
        username=session["username"],
        envios=envios
    )


@app.route("/seguimiento", methods=["GET", "POST"])
def seguimiento():

    envio = None
    historial = None

    if request.method == "POST":

        codigo = request.form.get("codigo", "").strip().upper()

        if codigo:
            resultado = get_shipment_by_code(codigo)

            if resultado:
                envio = dict(resultado)

                movimientos = get_shipment_history(envio["id"])
                historial = [dict(movimiento) for movimiento in movimientos]

                zona_argentina = ZoneInfo("America/Argentina/Buenos_Aires")

                fecha_utc = datetime.strptime(
                    envio["fecha_registro"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)

                envio["fecha_registro"] = fecha_utc.astimezone(
                    zona_argentina
                ).strftime("%d/%m/%Y %H:%M:%S")

                for movimiento in historial:
                    fecha_historial_utc = datetime.strptime(
                        movimiento["fecha_actualizacion"],
                        "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)

                    movimiento["fecha_actualizacion"] = fecha_historial_utc.astimezone(
                        zona_argentina
                    ).strftime("%d/%m/%Y %H:%M:%S")

            else:
                flash("No encontramos un envío con ese código.", "error")

        else:
            flash("Ingresá un código de seguimiento.", "error")

    return render_template(
        "seguimiento.html",
        envio=envio,
        historial=historial
    )

@app.route("/envios/registrar", methods=["GET", "POST"])
def registrar_envio():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        destinatario = request.form.get("destinatario", "").strip()
        direccion = request.form.get("direccion", "").strip()
        descripcion = request.form.get("descripcion", "").strip()

        # Validar campos obligatorios
        if not destinatario or not direccion:
            flash("El destinatario y la dirección son obligatorios.", "error")
            return redirect(url_for("registrar_envio"))

        # Generar código único de seguimiento
        codigo = "ENV-" + uuid.uuid4().hex[:10].upper()

        resultado = create_shipment(
            codigo,
            destinatario,
            direccion,
            descripcion
        )

        if resultado:
            flash(
                f"Envío registrado correctamente. Código: {codigo}",
                "success"
            )
            return redirect(url_for("dashboard"))

        flash("No se pudo registrar el envío. Intentá nuevamente.", "error")

    return render_template("registro.html")

@app.route("/envios/actualizar/<int:envio_id>", methods=["POST"])
def actualizar_estado(envio_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    nuevo_estado = request.form.get("estado", "").strip()
    observacion = request.form.get("observacion", "").strip()

    estados_validos = [
        "Pendiente",
        "En preparación",
        "En camino",
        "Entregado"
    ]

    if nuevo_estado not in estados_validos:
        flash("El estado seleccionado no es válido.", "error")
        return redirect(url_for("dashboard"))

    if not observacion:
        flash("Debés ingresar una observación.", "error")
        return redirect(url_for("dashboard"))

    resultado = update_shipment_status(
        envio_id,
        nuevo_estado,
        observacion
    )

    if resultado:
        flash("Estado del envío actualizado correctamente.", "success")
    else:
        flash("No se encontró el envío seleccionado.", "error")

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
