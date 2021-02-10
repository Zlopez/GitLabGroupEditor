# This is a script that updates projects properties in specific
# group on GitLab.

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


def create_group_query(group: str) -> gql:
    """
    Create query for GraphQL API.

    Params:
      group: Group name which we want to get.

    Returns:
      Query for GraphQL.
    """
    return gql(
        """
        query{{
            group(fullPath: "{group}") {{
                projects {{
                    nodes {{
                        id
                        visibility
                        mergeRequestsEnabled
                    }}
                }}
            }}
        }}
        """.format(group = group)
    )


def validate_result(result: dict) -> bool:
    """
    Validates the result retrieved from GraphQL.

    Params:
      result: Response retrieved from GraphQL

    Returns:
      Result of validation.
    """
    try:
        if result["group"]["projects"]["nodes"]:
            return True
    except TypeError:
        return False


def create_projects_mutation(projects: list, visibility: str, merge_requests_enabled: bool) -> gql:
    """
    Prepares GraphQL mutation for provided projects.

    Params:
      projects: List of projects to change.
      visibility: Visibility of the project, could be "private" or "public".
      merge_requests_enabled: Enable/disable merge requests on the project.

    Returns:
      GraphQL mutation.
    """
    result = "mutation{"
    for project in projects:
        result = result + """
        project(
            input: {{
                id: "{id}",
                visibility: "{visibility}",
                mergeRequestsEnabled: "{merge_requests_enabled}"
            }}
        ) {{
            project{{
                name
            }}
            errors
        }}
        """.format(
            id=project["id"],
            visibility=visibility,
            merge_requests_enabled=merge_requests_enabled
        )


    result = result + "}"
    return result


if __name__ == "__main__":
    # Let's add API key to header, otherwise only read access to API
    token = "foobar"
    headers = {
        "Authorization": "Bearer {token}".format(token=token)
    }
    url = "https://gitlab.com/api/graphql"
    group = "testgroup519"
    visibility = "private"
    merge_requests_enabled = False
    # Transport endpoint
    if headers:
        print("Using headers: {headers}".format(headers=headers))
        transport = AIOHTTPTransport(url=url, headers=headers)
    else:
        transport = AIOHTTPTransport(url=url)

    # Create a GraphQL client
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Prepare query
    query = create_group_query(group)

    # Execute the query
    result = client.execute(query)
    # print(result)

    # Get projects from the result
    if (validate_result(result)):
        projects = result["group"]["projects"]["nodes"]
    else:
        print("The response is missing the projects data: '{response}'".format(response = result))
        exit(1)

    # print(projects)

    # Prepare mutation
    mutation = create_projects_mutation(projects, visibility, merge_requests_enabled)
    print(mutation)

    # Execute the query
    #result = client.execute(mutation)
    #print(result)
