#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

ma = Marshmallow(app)
api = Api(app)

# Schema
class NewsletterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Newsletter
        load_instance = True

    title = ma.auto_field()
    published_at = ma.auto_field()

    url = ma.Hyperlinks({
        "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
        "collection": ma.URLFor("newsletters")
    })

newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# Routes
class Index(Resource):
    def get(self):
        return make_response({"index": "Welcome to the Newsletter RESTful API"}, 200)

class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(newsletters_schema.dump(newsletters), 200)

    def post(self):
        new_newsletter = Newsletter(
            title=request.form['title'],
            body=request.form['body']
        )
        db.session.add(new_newsletter)
        db.session.commit()
        return make_response(newsletter_schema.dump(new_newsletter), 201)

class NewsletterByID(Resource):
    def get(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        return make_response(newsletter_schema.dump(newsletter), 200)

    def patch(self, id):
        newsletter = Newsletter.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])
        db.session.commit()
        return make_response(newsletter_schema.dump(newsletter), 200)

    def delete(self, id):
        record = Newsletter.query.filter_by(id=id).first()
        db.session.delete(record)
        db.session.commit()
        return make_response({"message": "record successfully deleted"}, 200)

# Register resources
api.add_resource(Index, '/')
api.add_resource(Newsletters, '/newsletters', endpoint="newsletters")
api.add_resource(NewsletterByID, '/newsletters/<int:id>', endpoint="newsletterbyid")
