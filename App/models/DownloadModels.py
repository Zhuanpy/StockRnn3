from ..exts import db


class Download1MRecord(db.Model):

    __tablename__ = "download_1m_data"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)  # 股票名称
    market_code = db.Column(db.String(10), nullable=False)  # 股票市场代码
    code = db.Column(db.String(10), nullable=False)  # 股票代码
    es_code = db.Column(db.String(20))  # 东方财富股票代码
    es_download_status = db.Column(db.String(50))  # 东方财富下载状态
    txd_market_code = db.Column(db.String(10))  # Txd市场代码
    hs_market_code = db.Column(db.String(10))  # Hs市场代码
    classification = db.Column(db.String(20), nullable=False)  # 市场分类

    start_date = db.Column(db.Date, nullable=False)  # 数据记录开始日期
    end_date = db.Column(db.Date, nullable=False)  # 数据记录结束日期
    record_date = db.Column(db.Date, nullable=False)  # 数据记录的创建日期

    def __repr__(self):
        return (f"<Download1MRecord(id={self.id}, name='{self.name}', code='{self.code}', "
                f"es_code='{self.es_code}', es_download_status='{self.es_download_status}', "
                f"txd_market_code='{self.txd_market_code}', hs_market_code='{self.hs_market_code}', "
                f"classification='{self.classification}', end_date='{self.end_date}', record_date='{self.record_date}')>")

        # 类方法：通过 ID 更新并提交更改

    def update_and_commit(self, **kwargs):
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Error occurred:", e)
            raise

    @classmethod
    def update_by_id(cls, record_id, **kwargs):
        record = cls.query.get(record_id)
        if record:
            record.update_and_commit(**kwargs)
            return record
        else:
            print("Record not found")
            return None

