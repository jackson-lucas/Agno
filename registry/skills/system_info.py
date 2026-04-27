from agno.skills.loaders.local import LocalSkills

loader = LocalSkills(path='cookbook/05_agent_os/skills/sample_skills/system-info')
skills = loader.load()
system_info = skills[0] if skills else None
