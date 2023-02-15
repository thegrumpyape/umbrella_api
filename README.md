# Umbrella API

## Description

Umbrella API is a Python wrapper for the [Cisco Umbrella API](https://developer.cisco.com/docs/cloud-security/#!umbrella-introduction). It makes it easy to interact with the Cisco Umbrella API Policies endpoint and perform common tasks such as adding and removing domains from destination lists, retrieving destination lists, and more.

## Getting Started

### Installing

You can install the Umbrella API package using pip:

`pip install git+https://github.com/thegrumpyape/umbrella_api.git@main`

### Usage

Here's a simple example of how to use Umbrella API to retrieve a list of all destination lists:

```python
from umbrella_api.client import UmbrellaAPI

umbrella_api = UmbrellaApi(ident='client_id', secret='client_secret')

destination_lists = umbrella_api.destination_lists()

for result in destination_lists:
    print(result.name)
```

## Version History

* 0.1
    * Initial Release