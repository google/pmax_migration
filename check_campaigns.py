#!/usr/bin/env python
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This script queries the performance max migration status for a list of CIDs
 and returns the new performance max campaign reference if available."""
import argparse
import sys
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def get_status(client, customer_id):
  """Retrieves performance max status for a specific customer_id and prints
   out the details in the csv format customer id, ssc campaign, status, pmax campaign

  Args:
    client: A Google Ads API Client.
    customer_id: The external customer ID for the account.
  """
  ga_service = client.get_service("GoogleAdsService")

  query = f"""
    SELECT campaign.performance_max_upgrade.status,
     campaign.performance_max_upgrade.pre_upgrade_campaign,
     campaign.performance_max_upgrade.performance_max_campaign,
     campaign.name
     FROM campaign
     WHERE campaign.advertising_channel_sub_type = 'SHOPPING_SMART_ADS'
     """

  search_request = client.get_type("SearchGoogleAdsStreamRequest")
  search_request.customer_id = customer_id
  search_request.query = query
  stream = ga_service.search_stream(request=search_request)
  statuses = []
  for batch in stream:
    for row in batch.results:
      campaign = row.campaign
      if campaign.performance_max_upgrade.pre_upgrade_campaign:
        status_string = f"{customer_id}, {campaign.performance_max_upgrade.pre_upgrade_campaign},{campaign.performance_max_upgrade.status}, {campaign.performance_max_upgrade.performance_max_campaign}"
        statuses.append(status_string)
  return statuses

def main(client, customer_ids):
  """Gets all migration statuses for each CID and applies them w or w/o a prompt.
  Args:
    client: A Google Ads API Client.
    customer_ids: a list of customer ids.
  """

  for customer_id in customer_ids:
    # Uncomment below to log in directly on each account, vs at manager level.
    # googleads_client.login_customer_id = customer_id
    try:
      statuses = get_status(client, customer_id)
    except GoogleAdsException as x:
      print(f'Request with ID "{x.request_id}" failed with status '
            f'"{x.error.code().name}" and includes the following errors:')
      for e in x.failure.errors:
        print(f'\tError with message "{e.message}".')
        if e.location:
          for element in e.location.field_path_elements:
            print(f"\t\tOn field: {element.field_name}")
    for status_string in statuses:
      print(status_string)
      with open("campaign_statuses.txt", "a") as campaign_statuses:
        campaign_statuses.write(status_string + "\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Gets and applies pmax recommendations for list of CIDs")
  # The following argument(s) should be provided to run the example.
  parser.add_argument(
      "-c",
      "--customer_id",
      type=str,
      required=False,
      help="The Google Ads customer IDs as a comma separated string. (without dashes)",
  )
  parser.add_argument(
      "-p",
      "--path_config",
      type=str,
      required=True,
      help="The path for the google-ads.yaml configuration file.")
  # GoogleAdsClient will read the google-ads.yaml configuration file in the
  # home directory if none is specified.
  args = parser.parse_args()
  googleads_client = GoogleAdsClient.load_from_storage(
      version="v11", path=args.path_config)
  accounts = args.customer_id.replace(" ", "").split(",")
 
  main(googleads_client, accounts)