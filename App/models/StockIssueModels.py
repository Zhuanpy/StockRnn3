from ..exts import db


class Issue(db.Model):
    __tablename__ = 'stock_issue'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    solution = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="未解决")  # 状态：未解决，已解决等

    def __repr__(self):
        return f'<Issue {self.id} - {self.question}>'
