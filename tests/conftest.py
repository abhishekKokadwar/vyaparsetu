import os
os.environ["VYAPAR_LLM_DISABLED"] = "1"   # unit tests use the rule parser only
os.environ["VYAPAR_DB_DISABLED"] = "1"      # unit tests never touch the cloud database
