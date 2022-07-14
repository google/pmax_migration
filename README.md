# pMax Migration Command Line Tool

## Description

The script reads and applies recommendations for a list of comma separated CIDs.
Additional flags can be passed to customize the execution, or to call the script
programmatically to iterate over different credential sets. It uses the Google
Ads API V11, which includes the recommendation type for the PMAX Upgrade.

It processes each account sequentially and applies the recommendations. You
should run the process in manageable batches (<1000 CIDs per run) to ensure that
you do not hit quota limits for your developer token.

We recommend testing with a subset of accounts to ensure recommendations are
processed as expected and your platform supports the migrated campaigns without
issue.

## Usage

1.  Install Google Ads API Python client library.
2.  Get Developer token (in a manager account).
3.  Get Oauth ID/Secret pair.
4.  Get a Refresh token based on 3.
5.  Configure YAML file with the 2, 3 and 4.
6.  Set the Manager account ID in the YAML file to login with, or enable direct
    login for each account (see below under Accounts Access)
7.  Execute the script, passing in list of CIDs.

For ex:

```
python apply_recommendations.py --customer_id=111111,22222,33333 --path_config=/path/to/file
```

## Requirements

**Credentials**

The user must provide credentials consisting of:

*   Developer Token,
*   Oauth client Secret and ID.
*   A refresh token.

These should be passed in the yaml configuration file. If necessary, you can
have multiple yaml files. Each execution will use only 1 file, and you can
specify which file with the flag path_config.

**Google Ads API Client**

The latest
[Google Ads Python API Client](https://github.com/googleads/google-ads-python)
should be installed.

**Accounts Access**

The script may execute in two ways:

*   Log in on manager account level, by configuring the YAML file, to access all
    child accounts (default), or
*   Log in directly for each CID passed, by uncommenting line 96 in
    apply_recommendations.py, like below.

```
# Uncomment below to log in directly on each account, vs at manager level.
# googleads_client.login_customer_id = customer_id
```

Since the first option is more common for this type of usage, the script has it
by default. If you want to The Script executes on CID level, so the user should
have admin rights to all CIDs provided in the list. If one of the accounts
returns an 'unauthorized' error, the others will still execute.

## Flags

**--customer_id or -c**

This flag is required and will tell the script which accounts to get/apply
recommendations from. It should be comma separated, no quotes and an = sign or
space will work, as below.

`ex: --customer_id=11111,22222,33333 or -c 1111,22222`

**--path_config or -p**

If no yaml file path is passed, the tool will look for one in the home directory
(~/). Passing the yaml file path can be helpful if calling the script
programmatically over multiple sets of credentials, if necessary.

`ex: --path_config=/path/to/your/yaml or -p /path/to/yaml`

**--override_safe or -o**

By default, you'll receive a prompt to confirm the upgrade. You can switch this
off and execute without receiving a prompt

`ex: python apply_recommendations.py -c 11111 -p /path/to/yaml --override_safe`

**This is not an officially supported Google product.**

**Copyright 2022 Google LLC**
