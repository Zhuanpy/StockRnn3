from ..exts import db


# mystockrecord.basic_info_others_code;
class StockBasicInformationOthersCode(db.Model):
    __tablename__ = 'basic_info_others_code'
    # id  name    code  EsCode MarketCode EsDownload TxdMarket HsMarket
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    code = db.Column(db.String(20))
    EsCode = db.Column(db.String(20))
    MarketCode = db.Column(db.String(20))
    EsDownload = db.Column(db.String(20))
    TxdMarket = db.Column(db.String(20))
    HsMarket = db.Column(db.String(20))


# mystockrecord.basic_info_stock;
class StockBasicInformationStock(db.Model):
    __tablename__ = 'basic_info_stock'
    # id  name    code Classification
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    code = db.Column(db.String(20))
    Classification = db.Column(db.String(20))
