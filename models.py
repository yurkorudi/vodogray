from flask import current_app, has_app_context, has_request_context
from flask_sqlalchemy import SQLAlchemy

from i18n import get_locale


db = SQLAlchemy()


class Cottage(db.Model):
    __tablename__ = "cottages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    name_uk = db.Column(db.String(150), nullable=True)
    name_en = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_uk = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False, default=0)
    capacity = db.Column(db.Integer, nullable=True)
    features = db.Column(db.Text, nullable=True)
    features_uk = db.Column(db.Text, nullable=True)
    features_en = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    photos = db.relationship(
        "Photo",
        back_populates="cottage",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def localized_name(self):
        return localized_value(self, "name") or self.name

    @property
    def localized_description(self):
        return localized_value(self, "description") or self.description

    @property
    def localized_features(self):
        return localized_value(self, "features") or self.features

    @property
    def feature_list(self):
        return [item.strip() for item in (self.localized_features or "").splitlines() if item.strip()]


class Hall(db.Model):
    __tablename__ = "halls"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    name_uk = db.Column(db.String(150), nullable=True)
    name_en = db.Column(db.String(150), nullable=True)
    description = db.Column(db.Text, nullable=True)
    description_uk = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    price = db.Column(db.Integer, nullable=False, default=0)
    capacity = db.Column(db.Integer, nullable=True)
    booking_from = db.Column(db.String(80), nullable=True)
    features = db.Column(db.Text, nullable=True)
    features_uk = db.Column(db.Text, nullable=True)
    features_en = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    photos = db.relationship(
        "Photo",
        back_populates="hall",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def localized_name(self):
        return localized_value(self, "name") or self.name

    @property
    def localized_description(self):
        return localized_value(self, "description") or self.description

    @property
    def localized_features(self):
        return localized_value(self, "features") or self.features

    @property
    def feature_list(self):
        return [item.strip() for item in (self.localized_features or "").splitlines() if item.strip()]


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=True)
    image_url = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(150), nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    cottage_id = db.Column(db.Integer, db.ForeignKey("cottages.id"), nullable=True)
    hall_id = db.Column(db.Integer, db.ForeignKey("halls.id"), nullable=True)

    cottage = db.relationship("Cottage", back_populates="photos")
    hall = db.relationship("Hall", back_populates="photos")


def localized_value(model, field):
    lang = "uk"
    if has_app_context():
        lang = current_app.config["BABEL_DEFAULT_LOCALE"]
    if has_request_context():
        lang = get_locale()

    localized = getattr(model, f"{field}_{lang}", None)
    fallback_uk = getattr(model, f"{field}_uk", None)
    fallback_en = getattr(model, f"{field}_en", None)
    legacy = getattr(model, field, None)
    return localized or fallback_uk or fallback_en or legacy
