from openai import OpenAI
from tavily import TavilyClient
import json
import os
from github import Github

openai_api_key = os.environ.get('OPENAI_API_KEY')
tavily_api_key = os.environ.get('TAVILY_API_KEY')
moodle_token = os.environ.get('MOODLE_TOKEN')
git_token = os.environ.get('GIT_TOKEN')

client = OpenAI(api_key=openai_api_key)
tavily_client = TavilyClient(api_key=tavily_api_key)
g = Github(git_token)


# Function for getting repo name from Github
def get_all_repo_name():
    result = []
    for repo in g.get_user().get_repos():
        result.append(repo.name)
    return json.dumps(result)


# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", max_tokens=8000)
    return search_result


# Function for returning the content of a given repository
def get_content_given_repo(repo_name):
    repo = g.get_repo(f"{repo_name}")
    contents = repo.get_contents("")
    result = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            result.append(file_content)
    return json.dumps(f"{result}")


functions = [{
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Get information on recent events from the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string",
                              "description": "The search query to use."},
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_repo_name",
            "description": "Get all repo names from Github",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_content_given_repo",
            "description": "Get the content of a given repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_name": {
                        "type": "string",
                        "description": "The name of a repository, e.g. github-starter-course",
                    },
                },
                "required": ["repo_name"],
            },
        }
    }
]

function_lookup = {
    "tavily_search": tavily_search,
    "get_all_repo_name": get_all_repo_name,
    "get_content_given_repo": get_content_given_repo
}

## Create an assistant
#assistant = client.beta.assistants.create(
#    name="GitHub Assistant",
#    instructions="You are an assistant who has access to GitHub and the web.",
#    tools=functions,
#    model="gpt-3.5-turbo-0125"
#)


# Function to handle tool output submission
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = json.loads(tool.function.arguments)
        function_to_call = function_lookup[function_name]
        output = function_to_call(**function_args)
        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

