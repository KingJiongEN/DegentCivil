from typing import Dict, Union, List, Tuple
from .character import Character, CharacterList
from .drawing import Drawing, DrawingList
import time

class TradeRecord:
    def __init__(
            self, 
            buyer: Character,
            seller: Character, 
            resource_id: str, 
            remaining_budget: float,
            like_score: float, 
            emotion: str,
            market_price: float, 
            expected_price: float,
            final_price: float
            ) -> None:
        self.buyer = buyer
        self.seller = seller
        self.resource_id = resource_id
        self.remaining_budget = remaining_budget
        self.emotion = emotion
        self.timestamp = time.time()
        self.like_score = like_score
        self.market_price = market_price
        self.expected_price = expected_price
        self.final_price = final_price
    
    def __str__(self) -> str:
        return f"""[resource_id]: {self.resource_id}
[timestamp]: {self.timestamp}
[buyer]: {self.buyer.name}
[seller]: {self.seller.name}
[remaining_budget]: {self.remaining_budget}
[market_price]: {self.price}
[emotion]: {self.emotion}
[like score]: {self.like_score}
[expected_price]: {self.expected_price}
[final_price]: {self.final_price}"""
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, o: 'TradeRecord') -> bool:
        return self.seller == o.seller and self.resource_id == o.resource_id and self.timestamp == o.timestamp
    
    @staticmethod
    def to_str(trade_record: 'TradeRecord') -> str:
        return str(trade_record)

    @staticmethod
    def from_str(trade_record_str: str, character_list: CharacterList) -> 'TradeRecord':
        trade_record_str = trade_record_str.replace("[", "").replace("]", "")
        trade_record_str = trade_record_str.split("\n")
        trade_record_dict = {}
        for record in trade_record_str:
            key, value = record.split(":")
            trade_record_dict[key.strip()] = value.strip()
        buyer = character_list.get_character_by_name(trade_record_dict["buyer"])
        seller = character_list.get_character_by_name(trade_record_dict["seller"])
        trade_record = TradeRecord(
            buyer=buyer,
            seller=seller,
            resource_id=trade_record_dict["resource_id"],
            remaining_budget=float(trade_record_dict["remaining_budget"]),
            like_score=float(trade_record_dict["like_score"]),
            emotion=trade_record_dict["emotion"],
            market_price=float(trade_record_dict["market_price"]),
            expected_price=float(trade_record_dict["expected_price"]),
            final_price=float(trade_record_dict["final_price"])
        )
        return trade_record


class Trade:
    @staticmethod
    def make_trade(buyer: Character, seller: Character, resource_id: str, price: float, resource_type: str = "drawings", **kwargs) -> Tuple[bool, TradeRecord]:
        """Trade resources with another character. 
        
        Args:
            buyer (Character): The character that initiates the trade.
            seller (Character): The character that receives the trade.
            trade (Dict[str, float]): The trade resources. The key is the resource name, and the value is the amount.
        """
        if buyer.Gold < price:
            return False, None
        assert resource_type in ["drawings"], "Invalid resource type"
        origin_buyer_resource: DrawingList = buyer.__getattribute__(resource_type)
        origin_seller_resource: DrawingList = seller.__getattribute__(resource_type)
        resource = origin_seller_resource.get(resource_id)
        if not origin_buyer_resource.remove(resource):
            return False, None
        resource.owner = buyer
        origin_buyer_resource.add(resource)
        buyer.__setattr__(resource_type, origin_buyer_resource)
        seller.__setattr__(resource_type, origin_seller_resource)
        buyer.Gold -= price
        seller.Gold += price
        trade_record = TradeRecord(buyer=buyer, seller=seller, resource_id=resource_id, **kwargs)
        return True, trade_record