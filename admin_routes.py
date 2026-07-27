from functools import wraps

from flask_babel import _
from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from models import Cottage, Hall, Photo, db


admin_bp = Blueprint("admin", __name__)


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.admin"))
        return view(*args, **kwargs)

    return wrapped_view


@admin_bp.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        if login == current_app.config["ADMIN_LOGIN"] and password == current_app.config["ADMIN_PASS"]:
            session["admin_logged_in"] = True
            flash(_("Login successful."), "success")
            return redirect(url_for("admin.dashboard"))

        flash(_("Invalid login or password."), "danger")

    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/admin.html", mode="login")


@admin_bp.route("/admin/dashboard")
@admin_required
def dashboard():
    cottages = Cottage.query.order_by(Cottage.id.desc()).all()
    halls = Hall.query.order_by(Hall.id.desc()).all()
    photos = Photo.query.order_by(Photo.sort_order.asc(), Photo.id.desc()).all()
    return render_template(
        "admin/admin.html",
        mode="dashboard",
        cottages=cottages,
        halls=halls,
        photos=photos,
    )


@admin_bp.route("/admin/logout", methods=["POST"])
@admin_required
def logout():
    session.pop("admin_logged_in", None)
    flash(_("You have logged out of the admin panel."), "success")
    return redirect(url_for("admin.admin"))


@admin_bp.route("/admin/cottages", methods=["POST"])
@admin_required
def create_cottage():
    cottage = Cottage()
    fill_cottage(cottage)
    db.session.add(cottage)
    db.session.commit()
    flash(_("Cottage has been added."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/cottages/<int:cottage_id>", methods=["POST"])
@admin_required
def update_cottage(cottage_id):
    cottage = Cottage.query.get_or_404(cottage_id)
    fill_cottage(cottage)
    db.session.commit()
    flash(_("Cottage has been updated."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/cottages/<int:cottage_id>/delete", methods=["POST"])
@admin_required
def delete_cottage(cottage_id):
    cottage = Cottage.query.get_or_404(cottage_id)
    db.session.delete(cottage)
    db.session.commit()
    flash(_("Cottage has been deleted."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/halls", methods=["POST"])
@admin_required
def create_hall():
    hall = Hall()
    fill_hall(hall)
    db.session.add(hall)
    db.session.commit()
    flash(_("Hall has been added."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/halls/<int:hall_id>", methods=["POST"])
@admin_required
def update_hall(hall_id):
    hall = Hall.query.get_or_404(hall_id)
    fill_hall(hall)
    db.session.commit()
    flash(_("Hall has been updated."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/halls/<int:hall_id>/delete", methods=["POST"])
@admin_required
def delete_hall(hall_id):
    hall = Hall.query.get_or_404(hall_id)
    db.session.delete(hall)
    db.session.commit()
    flash(_("Hall has been deleted."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/photos", methods=["POST"])
@admin_required
def create_photo():
    photo = Photo()
    fill_photo(photo)
    db.session.add(photo)
    db.session.commit()
    flash(_("Photo has been added."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/photos/<int:photo_id>", methods=["POST"])
@admin_required
def update_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    fill_photo(photo)
    db.session.commit()
    flash(_("Photo has been updated."), "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/admin/photos/<int:photo_id>/delete", methods=["POST"])
@admin_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    db.session.delete(photo)
    db.session.commit()
    flash(_("Photo has been deleted."), "success")
    return redirect(url_for("admin.dashboard"))


def fill_cottage(cottage):
    cottage.name_uk = request.form.get("name_uk", "").strip()
    cottage.name_en = request.form.get("name_en", "").strip()
    cottage.description_uk = request.form.get("description_uk", "").strip()
    cottage.description_en = request.form.get("description_en", "").strip()
    cottage.name = cottage.name_uk or cottage.name_en or request.form.get("name", "").strip()
    cottage.description = cottage.description_uk or request.form.get("description", "").strip()
    cottage.price = to_int(request.form.get("price"))
    cottage.capacity = to_int(request.form.get("capacity")) or None
    cottage.features_uk = request.form.get("features_uk", "").strip()
    cottage.features_en = request.form.get("features_en", "").strip()
    cottage.features = cottage.features_uk or request.form.get("features", "").strip()
    cottage.is_active = request.form.get("is_active") == "on"


def fill_hall(hall):
    hall.name_uk = request.form.get("name_uk", "").strip()
    hall.name_en = request.form.get("name_en", "").strip()
    hall.description_uk = request.form.get("description_uk", "").strip()
    hall.description_en = request.form.get("description_en", "").strip()
    hall.name = hall.name_uk or hall.name_en or request.form.get("name", "").strip()
    hall.description = hall.description_uk or request.form.get("description", "").strip()
    hall.price = to_int(request.form.get("price"))
    hall.capacity = to_int(request.form.get("capacity")) or None
    hall.booking_from = request.form.get("booking_from", "").strip()
    hall.features_uk = request.form.get("features_uk", "").strip()
    hall.features_en = request.form.get("features_en", "").strip()
    hall.features = hall.features_uk or request.form.get("features", "").strip()
    hall.is_active = request.form.get("is_active") == "on"


def fill_photo(photo):
    photo.title = request.form.get("title", "").strip()
    photo.image_url = request.form.get("image_url", "").strip()
    photo.alt_text = request.form.get("alt_text", "").strip()
    photo.sort_order = to_int(request.form.get("sort_order"))
    photo.cottage_id = to_int(request.form.get("cottage_id")) or None
    photo.hall_id = to_int(request.form.get("hall_id")) or None

    if photo.cottage_id:
        photo.hall_id = None


def to_int(value):
    try:
        return int(value or 0)
    except ValueError:
        return 0
