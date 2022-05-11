# pMax Migration Command Line Tool

## Description

The tool reads and applies recommendations for a list of comma separated CIDs.
Additional flags can be passed to customize the execution, or call the script
programmatically to iterate over different credential sets.
It uses the Google Ads API.

## Usage

1. Install Google Ads API Python client.
2. Get Developer token.
3. Get Oauth ID/Secret pair.
4. Configure YAML file with 2 and 3.
5. Execute the script, passing in list of CIDs.

For ex:

`python apply_recommendations.py --customer_id=111111,22222,33333`
## Requirements

**Credentials**

The user must provide credentials consisting of:

  * Developer Token,
  * Oauth client Secret and ID.

These should be passed in the yaml configuration file.
The option to pass via flags will be added.

**Google Ads API Client**

The [Google Ads Python API Client](https://github.com/googleads/google-ads-python)
should be installed.

**Accounts Access**

The Script executes on CID level, so the user should have admin rights to all
CIDs provided in the list. If one of the accounts returns an 'unauthorized'
error, the others will still execute.

## Flags

**Customer IDs**

This flag is required and will tell the script which accounts to get/apply
recommendations from. It should be comma separated and the executing user must
have access:

`ex: --customer_id=11111,22222,33333 or -c 1111,22222`

**Yaml file path (Optional)**

If no yaml file path is passed, the tool will look for one in the home directory (~/). Passing the yaml file path can be helpful if calling the script programmatically over multiple sets of credentials.

`ex: --yaml_path=/path/to/your/yaml or -y /path/to/yaml`


