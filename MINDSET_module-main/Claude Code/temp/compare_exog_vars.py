"""
Compare how exog_vars.py vs exog_vars_SSP.py handle R and COU_ID
"""

print("=" * 80)
print("CHECKING exog_vars.py")
print("=" * 80)

with open('SourceCode/exog_vars.py', 'r') as f:
    lines = f.readlines()

print("\nLines that mention R:")
for i, line in enumerate(lines, 1):
    if 'self.R' in line and 'REG' not in line:
        print(f"{i}: {line.rstrip()}")

print("\nLines that mention COU_ID or SEC_ID:")
for i, line in enumerate(lines, 1):
    if 'COU_ID' in line or 'SEC_ID' in line:
        print(f"{i}: {line.rstrip()}")

print("\n" + "=" * 80)
print("CHECKING exog_vars_SSP.py")
print("=" * 80)

with open('SourceCode/exog_vars_SSP.py', 'r') as f:
    lines = f.readlines()

print("\nLines that mention R:")
for i, line in enumerate(lines, 1):
    if 'self.R' in line and 'REG' not in line:
        print(f"{i}: {line.rstrip()}")

print("\nLines that mention COU_ID or SEC_ID:")
for i, line in enumerate(lines, 1):
    if 'COU_ID' in line or 'SEC_ID' in line:
        print(f"{i}: {line.rstrip()}")
