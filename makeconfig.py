#Creates a config.yml file with client tokens for Reddit's API
from yaml import dump

#read values from user
tokens = dict()
print("Creating config.yml file:")
for str in ['client_id', 'client_secret', 'user_agent']:
    tokens[str] = input(str + "? ")
    
#dump file
with open("config.yml", "w") as f:
    dump(tokens, f)


