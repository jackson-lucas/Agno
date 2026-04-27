from agno.skills.loaders.local import LocalSkills

loader = LocalSkills(path='cookbook/02_agents/16_skills/sample_skills/git-workflow')
skills = loader.load()
git_workflow = skills[0] if skills else None
