import re

with open("src/ai/providers.py", "r") as f:
    text = f.read()

# Replace multiple CreateProjectParams duplicates with a single one plus the missing CreateEntitiesParams
pattern = r"class CreateProjectParams\(BaseModel\):.*?unit.*?default=\"minutes\"\)\n\n\n(?:class CreateProjectParams\(BaseModel\):.*?unit.*?default=\"minutes\"\)\n\n){0,2}\nclass CreateProjectParams\(BaseModel\):.*?unit.*?default=\"minutes\"\)\n\n"
# It looks like 3 identical classes
replacement = """class CreateProjectParams(BaseModel):
    title: str = Field(description=\"The name of the new project.\")
    target_value: int = Field(description=\"The target estimated effort value. If they specify hours, multiply by 60. Default is 0.\", default=0)
    unit: Optional[str] = Field(description=\"The unit of measurement (e.g. pages, pages, reps, hours, minutes). Default is minutes.\", default=\"minutes\")

class CreateEntitiesParams(BaseModel):
    projects: List[CreateProjectParams] = Field(description=\"List of new projects to create.\")

"""

text = re.sub(r'(class CreateProjectParams\(BaseModel\):[\s\S]*?unit:.*?\n\n)+', replacement, text)

# Just checking if there are duplicate extract_create_entities
text = re.sub(r'(    def extract_create_entities\(self, text: str\) -> Tuple\[Optional\[CreateEntitiesParams\], dict\]:[\s\S]*?return None, \{\}\n\n)+', r'\g<1>', text)

with open("src/ai/providers.py", "w") as f:
    f.write(text)
