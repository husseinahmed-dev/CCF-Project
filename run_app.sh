#!/bin/bash

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='hvs.CAESIB2qGGKhVdbtop1EC5k-hfvUCmfjeVW3RDPHQvapv9NDGh4KHGh2cy5XYU1McFZMMnJlTmJRYjhSazlQREpDanQ'

cd ProjectApi

dotnet restore

VAULT_SECRET_ID=$(cat vault-agent/secret-id) dotnet run