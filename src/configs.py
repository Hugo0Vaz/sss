from dataclasses import dataclass
from os.path import isfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

@dataclass
class Server:
    name: str
    host: str

@dataclass
class Team:
    name: str

@dataclass
class User:
    name: str
    teams: list[Team]
    pubkey: bytes | None
    privkey: bytes | None

@dataclass
class ACL:
    server: str
    access: list[User | Team]

def load_config(servers_file: str, users_file: str, acl_file: str) -> tuple[list[Server], list[User], list[Team], list[ACL]]:
    servers = load_servers(str(servers_file))
    users, teams = load_users_and_teams(str(users_file))
    acls = load_acls(str(acl_file), users, teams)

    return servers, users, teams, acls

def load_servers(path: str) -> list[Server]:
    """
    Returns the server from the configuration file
    """

    if not isfile(path):
        raise FileNotFoundError

    servers: list[Server] = []

    current_name = None
    current_host = None

    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                key, *rest = line.split()
                value = " ".join(rest)

                if key.lower() == "host":
                    if current_name and current_host:
                        servers.append(Server(name=current_name, host=current_host))

                    current_name = value
                    current_host = None

                elif key.lower() == "hostname":
                    current_host = value

            if current_name and current_host:
                servers.append(Server(name=current_name, host=current_host))

        return servers
    except Exception as e:
        raise e

def load_users_and_teams(path: str) -> tuple[list[User], list[Team]]:
    """
    Returns the users and teams from config file
    """
    users = []
    teams_dict = {}  # team_name -> Team object

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse line: "username: @team1, @team2"
            if ':' not in line:
                continue

            username, teams_str = line.split(':', 1)
            username = username.strip()

            # Parse teams
            team_names = [t.strip().lstrip('@') for t in teams_str.split(',')]
            team_names = [t for t in team_names if t]  # Filter empty strings

            # Create or get teams
            user_teams = []
            for team_name in team_names:
                if team_name not in teams_dict:
                    teams_dict[team_name] = Team(name=team_name)
                user_teams.append(teams_dict[team_name])

            # Create user with their teams
            pubkey, privkey = gen_keys()
            user = User(name=username, teams=user_teams, pubkey=pubkey, privkey=privkey)
            users.append(user)

    teams = list(teams_dict.values())
    return users, teams

def load_acls(path: str, users: list[User], teams: list[Team]) -> list[ACL]:
    """
    Returns the ACLs from the configuration file.
    
    File format:
    #server: user; @team
    servername: @team1, user1, @team2, user2, ...
    
    Args:
        path: Path to the ACL configuration file
        users: List of User objects to match against
        teams: List of Team objects to match against
    
    Returns:
        list[ACL]: List of ACL objects
    """
    acls = []

    # Create lookup dictionaries
    users_dict = {user.name: user for user in users}
    teams_dict = {team.name: team for team in teams}

    with open(path, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse line: "servername: @team1, user1, @team2"
            if ':' not in line:
                continue

            server, access_str = line.split(':', 1)
            server = server.strip()

            # Parse access entries
            entries = [e.strip() for e in access_str.split(',')]
            entries = [e for e in entries if e]  # Filter empty strings

            access = []
            for entry in entries:
                if entry.startswith('@'):
                    # It's a team
                    team_name = entry.lstrip('@')
                    if team_name in teams_dict:
                        access.append(teams_dict[team_name])
                else:
                    # It's a user
                    if entry in users_dict:
                        access.append(users_dict[entry])

            # Create ACL
            acl = ACL(server=server, access=access)
            acls.append(acl)

    return acls


def gen_keys() -> tuple[bytes, bytes]:
    """
    Generate public and private ed25519 SSH keys
    """

    private_key = ed25519.Ed25519PrivateKey.generate()

    private_ssh = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_key = private_key.public_key()
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    return public_ssh, private_ssh

