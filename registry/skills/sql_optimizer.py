from agno.skills.loaders.local import LocalSkills

loader = LocalSkills(path='skills/sql-optimizer')
skills = loader.load()
sql_optimizer = skills[0] if skills else None
