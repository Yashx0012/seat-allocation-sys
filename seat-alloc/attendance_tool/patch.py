with open("app.py", "r") as f:
    content = f.read()

# Revert my sed damage:
content = content.replace("{{", "{").replace("}}", "}")

# Now replace f""" with """ and add .replace('{COMMON_HEAD}', COMMON_HEAD)
content = content.replace('HTML_UPLOAD = f"""', 'HTML_UPLOAD = """')
content = content.replace('HTML_PREVIEW = f"""', 'HTML_PREVIEW = """')
content = content.replace('HTML_RESULT = f"""', 'HTML_RESULT = """')

# We need to process '{COMMON_HEAD}' before using it since we removed f
content = content.replace('COMMON_HEAD}\n</head>', 'COMMON_HEAD}\n</head>').replace('HTML_UPLOAD = """', 'HTML_UPLOAD = """'.replace('HTML_UPLOAD = """', 'HTML_UPLOAD = """\n').replace('HTML_PREVIEW = """', 'HTML_PREVIEW = """\n').replace('HTML_RESULT = """', 'HTML_RESULT = """\n'))

with open("app.py", "w") as f:
    f.write(content)
