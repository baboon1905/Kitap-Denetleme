#!/usr/bin/env python3
import ast

src = open('app.py', encoding='utf-8').read()
tree = ast.parse(src)

# Find all constants around line 1115
print("Strings around line 1110-1120:")
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        lineno = getattr(node, 'lineno', None)
        if 1110 <= lineno <= 1120:
            print(f"  Line {lineno}: {node.value[:80]}")
            
# Specifically look for "PDF endpoint geçerli" string
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if "PDF endpoint" in node.value:
            print(f"\n✓ Found 'PDF endpoint' string at Line {node.lineno}")
            print(f"  Full value: {node.value}")
            found = True

if not found:
    print("\n✗ 'PDF endpoint' string not found in AST")
    print("\nSearching for 'almadı' strings:")
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "almadı" in node.value:
                print(f"  Line {node.lineno}: {node.value}")
