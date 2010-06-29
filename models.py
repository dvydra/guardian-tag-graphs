from google.appengine.ext import db

class TagHistory(db.Model):
    name = db.StringProperty(required=True)
    related_section = db.StringProperty(required=True)
    data_date = db.DateTimeProperty()
    content_count = db.IntegerProperty()
