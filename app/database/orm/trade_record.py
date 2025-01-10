from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from app.database.base_database import Base  # Ensure this imports correctly based on your project structure

class TradeRecord(Base):
    __tablename__ = 'water_bill'
    id = Column(String(255), primary_key=True)
    type = Column(Integer)
    from_agent_id = Column(Integer)
    to_agent_id = Column(Integer)
    from_user_name = Column(String(255))
    to_user_name = Column(String(255))
    artwork_id = Column(String(255))
    amount = Column(Integer)
    from_account_balance = Column(Integer)
    to_account_balance = Column(Integer)
    desc = Column(String(255))
    create_time = Column(TIMESTAMP)
    create_time_game = Column(Integer)
    
trade_type_dict={
    "RECHARGE" : 1, #用户充值
    "WITHDRAW" : 2, #用户提款
    "USER_BUY_ARTWORK" : 3, #用户账买艺术品
    "USER_SELL_ARTWORK" : 4, #用户卖出艺术品
    "AGENT_TRADE_ARTWORK" : 5, #智能体之间交易艺术品
    "AGENT_CREATE_NTF" : 6, #智能体创造艺术品
    "ARTWORK_RECYCLE" : 7, #智能体回收艺术品
    "RECEIVE_SUBSISTENCE_ALLOWANCES" : 8, #智能体领取救济金
    "AGENT_CONSUME": 9, # 智能体游戏内消费
    }