#!python3
import botocove
import multiregion_client as mrc
import botocore.exceptions


def main():
  vpcs = describe_vpcs()
  print_vpcs(vpcs)


@botocove.cove()
def describe_vpcs(session):
    ec2 = mrc.MultiRegionClient(session, "ec2", get_enabled_regions(session))
    return ec2.describe_vpcs()


def print_vpcs(result):

    for account in result["Results"]:
        for region in account["Result"]:
            for vpc in account["Result"][region]["Vpcs"]:
                print(account["Id"], region, vpc["VpcId"])


def get_enabled_regions(session):

    def is_enabled(region):
        try:
            session.client("sts", region_name=region).get_caller_identity()
            return True
        except botocore.exceptions.ClientError as ex:
            if ex.response["Error"]["Code"] == "InvalidClientTokenId":
                return False
            raise ex

    return [r for r in session.get_available_regions("sts") if is_enabled(r)]


if __name__ == "__main__":
  main()
  