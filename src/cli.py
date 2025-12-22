from typing import List, Optional
from typing_extensions import Annotated

import configs

import typer
app = typer.Typer()

@app.command()
def rotate(
        servers_file: Annotated[Optional[str], typer.Option(help="Path to servers.txt file, defaults to $CWD/servers.txt")] = "./servers.txt",
        users_file: Annotated[Optional[str], typer.Option(help="Path to users.txt file, defaults to $CWD/users.txt")] = "./users.txt",
        acl_file: Annotated[Optional[str], typer.Option(help="Path to scl.txt file, defaults to $CWD/scl.txt")] = "./acl.txt",
        privkey: Annotated[Optional[str], typer.Option(help="Path to identity.txt file, defaults to $CWD/identity.txt")] = "./privkey.txt",
        pubkey: Annotated[Optional[str], typer.Option(help="Path to identity.txt file, defaults to $CWD/identity.txt")] = "./pubkey.txt",
        ):

    servers, users, teams, acls = configs.load_config(str(servers_file), str(users_file), str(acl_file))

    for server in servers:
        print(f"Generating authorized_keys for: {server.name}")

        # deploy_authorized_keys(gen_authorized_keys(users, teams, acls), server)
        gen_authorized_keys(server, users, acls, str(pubkey))

def gen_authorized_keys(
        server: configs.Server,
        users: list[configs.User],
        acls: list[configs.ACL],
        ssss_pubkey: str,
        ):
    """
    Function to generate authorized keys from users, teams and acls
    """

    allowed_users = get_users_with_access(server, acls, users)

    au = "-"
    for i in allowed_users:
        au = f"{au}"
        au = au + i.name + " \n-"

    print(f"Granting access in {server.name} to: \n {au}")

def get_users_with_access(server: configs.Server, acls: list[configs.ACL], all_users: list[configs.User]) -> list[configs.User]:
    """Returns a list of users that have access to the specified server."""
    
    # Find the ACL for this server
    server_acl = next((acl for acl in acls if acl.server == server.name), None)
    
    if not server_acl:
        return []
    
    users_dict = {}  # name -> User object
    
    for entry in server_acl.access:
        if isinstance(entry, configs.User):
            users_dict[entry.name] = entry
        elif isinstance(entry, configs.Team):
            for user in all_users:
                if entry in user.teams:
                    users_dict[user.name] = user
    
    return list(users_dict.values())
