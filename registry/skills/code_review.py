from agno.skills.loaders.local import LocalSkills

loader = LocalSkills(path='cookbook/02_agents/16_skills/sample_skills/code-review')
skills = loader.load()
code_review = skills[0] if skills else None
