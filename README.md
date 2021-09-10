# AWS Boto Multiregion Client

A boto3 client that queries multiple regions and returns all results in a single response.

It doesn't wrap an existing client. Instead it takes a session and creates one client for each region to query. When an API method is called on this client, the method call is dispatched to each region's client.

The closest existing tools that provide similar solutions are [awsls](https://github.com/jckuester/awsls) and [botocove](https://github.com/connelldave/botocove).

awsls is a command-line tool that allows you to list resources across multiple regions and CLI profiles. It uses Terraform's AWS provider to retrieve all resources and properties.

botocove is a Python library that allows you to execute boto3 functions across all accounts in an organization. It decorates a function that takes a boto3 session.

## Example

To use it, pass a boto3 session, the service, and the regions to query.

```python
import boto3

import multiregion_client as mr

ec2 = mr.MultiRegionClient(boto3.Session(), "ec2", ["eu-west-1", "eu-west-2"])

result = ec2.describe_vpcs()

# List all resources for a single region.
# The output shape is the same as that of a normal client.
result["eu-west-1"]["Vpcs"]

# List all resources from all regions.
# Again, the output shape is the same as that of a normal client,
# which is to say that the region information in the output is lost.
[resource for regional_result in result.values() for resource in regional_result["Vpcs"]]

# List all resources from all regions and show the region of each resource.
# The output shape extends that of a normal client by adding a RequestRegion
# key to each resource.
[
    {**resource, **{"RequestRegion": region}}
        for region, regional_result in result.items()
            for resource in regional_result["Vpcs"]
]
```

Example output in IPython in an account with default subnets:

```text
In [5]: result["eu-west-1"]["Vpcs"]
Out[5]: 
[{'CidrBlock': '172.31.0.0/16',
  'DhcpOptionsId': 'dopt-57e3ef31',
  'State': 'available',
  'VpcId': 'vpc-45d20f3c',
  'OwnerId': '480783779961',
  'InstanceTenancy': 'default',
  'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-1e915474',
    'CidrBlock': '172.31.0.0/16',
    'CidrBlockState': {'State': 'associated'}}],
  'IsDefault': True}]

In [6]: [resource for regional_result in result.values() for resource in regional_result["Vpcs"]]
Out[6]: 
[{'CidrBlock': '172.31.0.0/16',
  'DhcpOptionsId': 'dopt-57e3ef31',
  'State': 'available',
  'VpcId': 'vpc-45d20f3c',
  'OwnerId': '480783779961',
  'InstanceTenancy': 'default',
  'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-1e915474',
    'CidrBlock': '172.31.0.0/16',
    'CidrBlockState': {'State': 'associated'}}],
  'IsDefault': True},
 {'CidrBlock': '172.31.0.0/16',
  'DhcpOptionsId': 'dopt-d2a794ba',
  'State': 'available',
  'VpcId': 'vpc-1713487f',
  'OwnerId': '480783779961',
  'InstanceTenancy': 'default',
  'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-910d3ef9',
    'CidrBlock': '172.31.0.0/16',
    'CidrBlockState': {'State': 'associated'}}],
  'IsDefault': True}]

In [7]: [
   ...:     {**resource, **{"RequestRegion": region}}
   ...:         for region, regional_result in result.items()
   ...:             for resource in regional_result["Vpcs"]
   ...: ]
Out[7]: 
[{'CidrBlock': '172.31.0.0/16',
  'DhcpOptionsId': 'dopt-57e3ef31',
  'State': 'available',
  'VpcId': 'vpc-45d20f3c',
  'OwnerId': '480783779961',
  'InstanceTenancy': 'default',
  'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-1e915474',
    'CidrBlock': '172.31.0.0/16',
    'CidrBlockState': {'State': 'associated'}}],
  'IsDefault': True,
  'RequestRegion': 'eu-west-1'},
 {'CidrBlock': '172.31.0.0/16',
  'DhcpOptionsId': 'dopt-d2a794ba',
  'State': 'available',
  'VpcId': 'vpc-1713487f',
  'OwnerId': '480783779961',
  'InstanceTenancy': 'default',
  'CidrBlockAssociationSet': [{'AssociationId': 'vpc-cidr-assoc-910d3ef9',
    'CidrBlock': '172.31.0.0/16',
    'CidrBlockState': {'State': 'associated'}}],
  'IsDefault': True,
  'RequestRegion': 'eu-west-2'}]
```

## Combining with botocove for cross region and cross account queries

It is possible to combine it with this client to query all accounts and regions. See botocove_test.py for an example. It lists all the VPCs in all the enabled regions of all the member accounts in the organization.

The botocove test uses a get_enabled_regions function to avoid failures from querying disabled functions. This function is generally useful and could be split out.

```
$ poetry run python botocove_test.py
111111111111 ap-northeast-1 vpc-11111111
111111111111 ap-northeast-2 vpc-22222222
111111111111 ap-northeast-3 vpc-33333333
...
222222222222 ap-northeast-1 vpc-44444444
222222222222 ap-northeast-2 vpc-55555555
222222222222 ap-northeast-3 vpc-66666666
....
```
