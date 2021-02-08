# This is a script that updates projects properties in specific
# group on GitLab.

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def create_group_query(group: str):
    return gql(
        """
        query{{
            group(fullPath: "{group}") {{
                projects {{
                    nodes {{
                        name
                        fullPath
                        visibility
                        mergeRequestsEnabled
                    }}
                }}
            }}
        }}
        """.format(group = group)
    )

if __name__ == "__main__":
    # Let's add API key to header, otherwise only read access to API
    header = {}
    url = "https://gitlab.com/api/graphql"
    group = "testgroup519"
    # Transport endpoint
    if header:
        transport = AIOHTTPTransport(url=url, headers=headers)
    else:
        transport = AIOHTTPTransport(url=url)

    # Create a GraphQL client
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Prepare query
    query = create_group_query(group)

    # Execute the query
    result = client.execute(query)
    print(result)
