from agno.agent import Agent
from agno.team.team import Team

def print_metrics_agent(agent: Agent):
    from rich.pretty import pprint
    # Print metrics per message
    if agent.run_response.messages:
        for message in agent.run_response.messages:
            if message.role == "assistant":
                if message.content:
                    print(f"Message: {message.content}")
                elif message.tool_calls:
                    print(f"Tool calls: {message.tool_calls}")
                print("---" * 5, "Metrics", "---" * 5)
                pprint(message.metrics)
                print("---" * 20)

    # Print the aggregated metrics for the whole run
    print("---" * 5, "Collected Metrics", "---" * 5)
    pprint(agent.run_response.metrics)
    # Print the aggregated metrics for the whole session
    print("---" * 5, "Session Metrics", "---" * 5)
    pprint(agent.session_metrics)

def print_metrics_team(team: Team):
    from rich.pretty import pprint
    # Print metrics per message
    if team.run_response.messages:
        for message in team.run_response.messages:
            if message.role == "assistant":
                if message.content:
                    print(f"Message: {message.content}")
                elif message.tool_calls:
                    print(f"Tool calls: {message.tool_calls}")
                print("---" * 5, "Metrics", "---" * 5)
                pprint(message.metrics)
                print("---" * 20)
    # Print aggregated team leader metrics
    print("---" * 5, "Aggregated Metrics of Team Agent", "---" * 5)
    pprint(team.run_response.metrics)

    # Print team leader session metrics
    print("---" * 5, "Session Metrics", "---" * 5)
    pprint(team.session_metrics)

    # Print team member message metrics
    print("---" * 5, "Team Member Message Metrics", "---" * 5)
    if team.run_response.member_responses:
        for member_response in team.run_response.member_responses:
            if member_response.messages:
                for message in member_response.messages:
                    if message.role == "assistant":
                        if message.content:
                            print(f"Message: {message.content}")
                        elif message.tool_calls:
                            print(f"Tool calls: {message.tool_calls}")
                        print("---" * 5, "Metrics", "---" * 5)
                        pprint(message.metrics)
                        print("---" * 20)

    # Print full team session metrics (including all members)
    print("---" * 5, "Full Team Session Metrics", "---" * 5)
    pprint(team.full_team_session_metrics)