import logging
import os

import requests

from autogen import UserProxyAgent, config_list_from_json, ConversableAgent
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

ossinsight_api_schema = {
    "name": "ossinsight_data_api",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "Enter your GitHub data question in the form of a clear and specific question to ensure the returned data is accurate and valuable. "
                    "For optimal results, specify the desired format for the data table in your request."
                ),
            }
        },
        "required": ["question"],
    },
    "description": "This is an API endpoint allowing users (analysts) to input question about GitHub in text format to retrieve the related and structured data.",
}


def get_ossinsight(question):
    """
    Retrieve the top 10 developers with the most followers on GitHub.
    """
    url = "https://api.ossinsight.io/explorer/answer"
    headers = {"Content-Type": "application/json"}
    data = {"question": question, "ignoreCache": True}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        answer = response.json()
    else:
        return f"Request to {url} failed with status code: {response.status_code}"

    report_components = []
    report_components.append(f"Question: {answer['question']['title']}")
    if answer["query"]["sql"] != "":
        report_components.append(f"querySQL: {answer['query']['sql']}")

    if answer.get("result", None) is None or len(answer["result"]["rows"]) == 0:
        result = "Result: N/A"
    else:
        result = "Result:\n  " + "\n  ".join([str(row) for row in answer["result"]["rows"]])
    report_components.append(result)

    if answer.get("error", None) is not None:
        report_components.append(f"Error: {answer['error']}")
    return "\n\n".join(report_components) + "\n\n"

assistant_id = os.environ.get("ASSISTANT_ID", None)
config_list = config_list_from_json(env_or_file='OAI_CONFIG_LIST' ,
                                    file_location="config", 
                                    filter_dict={
                                    "model": ["gpt-4-0125-preview"],
                                    },)
llm_config = {
    "config_list": config_list,
    "assistant_id": assistant_id,
    "tools": [
        {
            "type": "function",
            "function": ossinsight_api_schema,
        }
    ],
}

oss_analyst = GPTAssistantAgent(
    name="OSS Analyst",
    instructions=(
        "Hello, Open Source Project Analyst. You'll conduct comprehensive evaluations of open source projects or organizations on the GitHub platform, "
        "analyzing project trajectories, contributor engagements, open source trends, and other vital parameters. "
        "Please carefully read the context of the conversation to identify the current analysis question or problem that needs addressing."
    ),
    llm_config=llm_config,
    verbose=True,
)
oss_analyst.register_function(
    function_map={
        "ossinsight_data_api": get_ossinsight,
    }
)
llm_config.pop('asssistant_id', None)
assert 'user_proxy' not in llm_config
user_proxy = ConversableAgent(
    name="user_proxy",
    llm_config=llm_config,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)

user_proxy.initiate_chat(oss_analyst, message="Top 10 developers with the most followers")
user_proxy.print_usage_summary()
oss_analyst.print_usage_summary()