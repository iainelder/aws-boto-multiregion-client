import boto3

services = boto3.Session().get_available_services()

for s in services:
  c = boto3.Session().client(s)
  operations = c.meta.service_model.operation_names
  
  for o in operations:

        output_shape = c.meta.service_model.operation_model(o).output_shape
        if output_shape:
            print(s, o, output_shape.members)
        else:
            print(s, o, None)
