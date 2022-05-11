from app import db


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    title = db.Column(db.Unicode(255), nullable=False, server_default=u'')
    requested_at = db.Column(db.DateTime())
    drafted_by = db.Column(db.Integer(), db.ForeignKey('users.id'))
    sn = db.Column(db.Unicode(20), server_default=u'')

    @classmethod
    def gen_sn(cls, report_id: int, length: int = 4, prefix: str = u'高') -> str:
        if len(str(report_id)) > length:
            raise Exception(f'The length of maximum report_id has been greater than {length}.')

        return prefix + str(report_id).zfill(length)
