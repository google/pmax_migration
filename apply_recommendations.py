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

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_recommendations(client, customer_id):
  """Retrieve recommendations for a specific customer_id.
     The recommendation type will be replaced once pMax is launched.
  """

  ga_service = client.get_service("GoogleAdsService")
  campaign_filter = ""
  query = f"""
    SELECT
      recommendation.type,
      recommendation.campaign,
      recommendation.resource_name
    FROM recommendation
    WHERE recommendation.type = KEYWORD
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


def apply_recommendation(client, customer_id, resource_name):
  recommendation_service = client.get_service("RecommendationService")
  apply_recommendation_operation = client.get_type(
      "ApplyRecommendationOperation")
  apply_recommendation_operation.resource_name = resource_name
  recommendation_response = recommendation_service.apply_recommendation(
      customer_id=customer_id, operations=[apply_recommendation_operation])
  return recommendation_response


def main(client, customer_id):
  recommendations = get_recommendations(client, customer_id)
  print("Total Recommendations available for CID {customer_id}: ",
        len(recommendations))
  confirmation = input(f"Apply all recommendations for CID {customer_id}? (y/n)"
                      ).lower().strip()
  while confirmation not in ("y", "n"):
    confirmation = input("Invalid answer. Please confirm with 'y' or 'n'.")
  if confirmation == "n":
    sys.exit("Exiting, no recommndations applied.")
  elif confirmation == "y":
    for recommendation in recommendations:
      response = apply_recommendation(client, customer_id, recommendation)
      print(f"Recommendation applied")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description="Lists TEXT_AD recommendations for specified customer.")
  # The following argument(s) should be provided to run the example.
  parser.add_argument(
      "-c",
      "--customer_id",
      type=str,
      required=False,
      help="The Google Ads customer ID.",
  )
  parser.add_argument(
      "-p",
      "--path_config",
      type=str,
      required=True,
      help="The full path for the google-ads.yaml configuration file.")

  # GoogleAdsClient will read the google-ads.yaml configuration file in the
  # home directory if none is specified.
  args = parser.parse_args()
  googleads_client = GoogleAdsClient.load_from_storage(
      version="v10", path=args.path_config)

  for account in args.customer_id.replace(" ", "").split(","):
    try:
      googleads_client.login_customer_id = account
      main(googleads_client, account)
    except GoogleAdsException as ex:
      print(f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:')
      for error in ex.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
          for field_path_element in error.location.field_path_elements:
            print(f"\t\tOn field: {field_path_element.field_name}")
