from ..exts import db


class Top500FundRecord(db.Model):
    """
    数据库模型：Top500 基金持仓记录
    """
    __tablename__ = "recordtopfunds500"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 自增主键
    name = db.Column(db.String(255), nullable=False)  # 基金名称，长度增加到255以支持完整基金名
    code = db.Column(db.String(50), nullable=False)  # 基金代码，长度增加到50支持更长格式
    selection = db.Column(db.Integer, nullable=False, default=0)  # 1代表选择，0代表未选择
    status = db.Column(db.Text, nullable=False)  # 基金状态下载状态
    date = db.Column(db.Date, nullable=False)  # 基金持仓日期

    def __repr__(self):
        """
        返回对象的字符串表示，便于调试和日志记录
        """
        return (
            f"<Top500FundPositions(id={self.id}, name={self.name}, code={self.code}, "
            f"selection={self.selection}, status={self.status}, date={self.date})>"
        )

    @staticmethod
    def validate_selection(value):
        """
        校验 selection 字段是否合法。
        :param value: int 1 或 0
        :raises ValueError: 如果值不合法
        """
        if value not in (0, 1):
            raise ValueError("selection 字段只能是 0 或 1")

    def update_by_id(self, record_id, status, date):
        """
        根据记录 ID 更新状态和日期。
        """
        record = Top500FundRecord.query.get(record_id)
        if record:
            record.status = status
            record.date = date
            db.session.commit()
