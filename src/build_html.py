import json
def build_html(data, output_path):
  with open('templates/template.html' , 'r') as f:
    template = f.read()
    template = template.replace('/*<mock_data>*/', json.dumps(data)[1:-1]) # indexing removes start end {}

    with open(output_path, 'w') as out_file:
      out_file.write(template)