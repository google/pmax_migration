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
"""This script gets all recommendations for a list of CIDs and applies them."""

import argparse
import sys

from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_recommendations(client, customer_id):
  """Retrieves recommendations for a specific customer_id.

  The recommendation type will be replaced once pMax is launched.

  Args:
    client: A Google Ads API Client.
    customer_id: The external customer ID for the account.

  Returns:
    recommendations: A list with recommendation IDs for the account.
  """

  ga_service = client.get_service("GoogleAdsService")
  campaign_filter = ""
  query = f"""
    SELECT
      recommendation.type,
      recommendation.campaign,
      recommendation.resource_name
    FROM recommendation
    WHERE recommendation.type = 'UPGRADE_SMART_SHOPPING_CAMPAIGN_TO_PERFORMANCE_MAX'
    {campaign_filter}
    """

  search_request = client.get_type("SearchGoogleAdsStreamRequest")
  search_request.customer_id = customer_id
  search_request.query = query
  stream = ga_service.search_stream(request=search_request)
  recommendations = []
  for batch in stream:
    for row in batch.results:
      recommendation = row.recommendation
      recommendations.append(recommendation.resource_name)
  return recommendations


def apply_recommendations(client, customer_id, recommendations):
  """Applies a list of recommendations for a customer_id.

  Args:
    client: A Google Ads API Client.
    customer_id: The external customer ID for the account.
    recommendations: a list with recommendation resources.

  Returns:
    recommendations_response: API response message with results[] and errors.
  """
  recommendation_operations = []
  recommendation_service = client.get_service("RecommendationService")
  for recommendation in recommendations:
    apply_recommendation_operation = client.get_type(
        "ApplyRecommendationOperation")
    apply_recommendation_operation.resource_name = recommendation
    recommendation_operations.append(apply_recommendation_operation)
  recommendations_response = recommendation_service.apply_recommendation(
      customer_id=customer_id, operations=recommendation_operations)
  return recommendations_response


def main(client, customer_ids, override_safe):
  """Gets all recommendations for each CID and applies them w or w/o a prompt.

  Args:
    client: A Google Ads API Client.
    customer_ids: a list of customer ids.
    override_safe: receive no prompt for confirmation and apply directly.
  """
  all_recommendations = {}
  for customer_id in customer_ids:
    # Uncomment below to log in directly on each account, vs at manager level.
    # googleads_client.login_customer_id = customer_id
    all_recommendations[customer_id] = []
    try:
      recommendations = get_recommendations(client, customer_id)
      all_recommendations[customer_id] = recommendations
    except GoogleAdsException as x:
      print(f'Request with ID "{x.request_id}" failed with status '
            f'"{x.error.code().name}" and includes the following errors:')
      for e in x.failure.errors:
        print(f'\tError with message "{e.message}".')
        if e.location:
          for element in e.location.field_path_elements:
            print(f"\t\tOn field: {element.field_name}")

  print("Total Recommendations found per CID:")
  total_recommendations = 0
  for customer_id in all_recommendations:
    total_recommendations += len(all_recommendations[customer_id])
    print(
        f"{customer_id}: {len(all_recommendations[customer_id])} recommendations"
    )
  if total_recommendations == 0:
    print("No recommendations found, terminating.")
    return
  if override_safe:
    confirmation = "y"
  else:
    confirmation = input("Apply all recommendations? (y/n)").lower().strip()

  while confirmation not in ("y", "n"):
    confirmation = input("Invalid answer. Please confirm with 'y' or 'n'.")
  if confirmation == "n":
    sys.exit("No recommndations applied.")
  elif confirmation == "y":
    for customer_id in all_recommendations:
      if not all_recommendations[customer_id]:
        print(f"CID: {customer_id}: 0 recommendations available, 0 applied. ")
      else:
        response = apply_recommendations(client, customer_id,
                                         all_recommendations[customer_id])
        print(
            f"CID: {customer_id} - total recommendations applied:{len(all_recommendations[customer_id])}"
        )
        with open("campaign_ids.txt", "a") as campaign_ids:
          campaign_ids.write(customer_id + "\n")
          campaign_ids.write(str(response) + "\n")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Gets and applies pmax recommendations for list of CIDs")
  # The following argument(s) should be provided to run the example.
  parser.add_argument(
      "-c",
      "--customer_id",
      type=str,
      required=False,
      help="The Google Ads customer ID. (without dashes)",
  )
  parser.add_argument(
      "-p",
      "--path_config",
      type=str,
      required=True,
      help="The path for the google-ads.yaml configuration file.")
  parser.add_argument(
      "-o",
      "--override_safe",
      action="store_true",
      help="No prompt before applying Recommendation for each CID.")

  # GoogleAdsClient will read the google-ads.yaml configuration file in the
  # home directory if none is specified.
  args = parser.parse_args()
  googleads_client = GoogleAdsClient.load_from_storage(
      version="v11", path=args.path_config)
  accounts = args.customer_id.replace(" ", "").split(",")
  main(googleads_client, accounts, args.override_safe)
