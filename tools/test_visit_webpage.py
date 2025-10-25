from visit_webpage import Input, execute

# Create input data
data = Input(url="https://www.telegraaf.nl")

# Run tool
result = execute(data)

# Print output
# print(result.json(indent=2))

print(result.model_dump_json(indent=2))
