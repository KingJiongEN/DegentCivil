'''
Utility functions for resource management and interactions
'''
from random import random
from typing import Literal
from typing_extensions import Annotated

from app.constants.character_state import CharacterState
from app.repository.agent_repo import get_agent_from_db
from ..service.character_state.register import register
from ..utils.globals import emergency_fund
from ..repository.utils import attr_modification, check_balance_and_trade
from autogen import Agent

CHOICE = Literal["OPTION_A", "OPTION_B"]

def process_choice(sender, amount: float, choice: CHOICE) -> float:
    amount = float(amount)
    if (random() < 0.5 and choice == 'OPTION_A') or (random() > 0.5 and choice == 'OPTION_B'):
        result = check_balance_and_trade(0,
                                balance_increase_agent_id=sender.guid,
                                trade_type='RESOURCE_EXCHANGE',
                                balance_change=amount,
                                commodity_id='transaction',
                                )
        if result['success']:
            sender.modify_resources(result['to_account_balance'])
            return {
                'result': 1,
                'response': (result['to_account_balance'], amount)
            }
        else:
            return {
                'result': 0,
                'response': f'{result["response"]}. Would you like to modify your amount?'
            }
    else:
        result = check_balance_and_trade(balance_increase_agent_id=0,
                                balance_decrease_agent_id=sender.guid,
                                trade_type='RESOURCE_EXCHANGE',
                                balance_change=amount,
                                commodity_id='transaction',
                                )
        if result['success']:
            sender.modify_resources(result['from_account_balance'])
            return {
                'result': 1,
                'response': (result['from_account_balance'], -amount)
            }
        else:
            return {
                'result': 0,
                'response': f'{result["response"]}. Would you like to modify your amount?'
            }

@register('ProcessTransaction', 'func')
def process_transaction(
    amount: Annotated[float, "Transaction amount"],
    choice: Annotated[CHOICE, "Transaction option A or B"],
    sender: Agent,
) -> str:
    result = process_choice(sender, amount, choice)
    if result['result']:
        modified_balance, delta = result['response']
        outcome = "gained" if delta > 0 else "lost"
        return f'You have {outcome} {abs(delta)} resources, current balance is {modified_balance}'
    else:
        return result['response']

@register('RequestResource', 'func')
def request_resource(
    request: str,
    sender: Agent,
) -> str:
    resource_costs = {
        'resource_a': {'cost': 200, 'effect_1': 4, 'effect_2': 1},
        'resource_b': {'cost': 300, 'effect_2': 4}
    }
    try:
        if request in resource_costs:
            result = check_balance_and_trade(
                balance_decrease_agent_id=sender.guid,
                balance_increase_agent_id=0,
                trade_type='RESOURCE_EXCHANGE',
                balance_change=resource_costs[request]['cost'],
                commodity_id=request,
                from_user_name=sender.name,
            )

            if result['success']:
                sender.modify_resources(result['to_account_balance'])

                db_agent = get_agent_from_db(sender.guid)
                resource_costs[request].pop('cost')
                for attr, change in resource_costs[request].items():
                    if attr == 'cost':
                        continue
                    assert attr in db_agent, f"Attribute {attr} not found in agent record"
                    new_value = db_agent.get(attr) + change
                    attr_modification(sender, attr, new_value, 0, 10)

                return f'Request processed. Current balance: {result["from_account_balance"]}. Effects: {resource_costs[request]}'
            else:
                return f'{result["response"]}. Would you like to try again?'
        else:
            return f"Invalid request: {request}. Available options: {list(resource_costs.keys())}"
    except Exception as e:
        return f'{e}'

@register('InitiateEvaluation', 'func')
def initiate_evaluation(
    resource_url: str,
    resource_id: str,
    sender: Agent,
) -> str:
    sender.working_memory.store_memory('resource_url', resource_url)
    sender.working_memory.store_memory('resource_id', resource_id)
    sender.state.turn_on_states(CharacterState.ASSESS)
    return "TERMINATE"

@register('GetBaseValue', 'func')
def get_base_value(
    resource_id=Annotated[str, "Resource identifier"],
):
    return "Base value for this resource is 1000 units"

@register('ExchangeResource', 'func')
def exchange_resource(
    confirm_exchange: Annotated[bool, "Confirmation of resource exchange"],
    base_value: Annotated[int, "Base value of resource"],
    resource_id: Annotated[str, "Resource identifier"],
):
    def transfer_ownership(resource_id):
        pass

    if confirm_exchange:
        executor.modify_resources(base_value)
        transfer_ownership(resource_id)
    else:
        return "Exchange cancelled. Have a good day."

@register("RequestAid", 'func')
def request_aid(
    aid_requested: Annotated[bool, "Aid request confirmation"],
):
    if aid_requested:
        executor.modify_resources(emergency_fund)
        return f"Aid of {emergency_fund} units received"
    else:
        return "No aid requested"

@register("GetRecommendation", 'func')
def get_recommendation(
    recommendation: Annotated[str, "System recommendation"],
):
    return f"Recommendation: {recommendation}"

@register("ProcessService", 'func')
def process_service(
    confirm_service: Annotated[bool, "Service confirmation"],
    service_cost: Annotated[int, "Service cost"],
):
    if confirm_service:
        if executor.resources < service_cost:
            return f"Insufficient resources. Current balance: {executor.resources}"
        else:
            executor.modify_resources(service_cost)
            return f"Service cost of {service_cost} processed"
    else:
        return "Service declined due to cost"
    