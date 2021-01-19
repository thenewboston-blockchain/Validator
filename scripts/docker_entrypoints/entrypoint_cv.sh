#!/bin/sh
set -e

echo "Waiting for postgres..."
until nc -z $POSTGRES_HOST 5432 > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL started"

init_node() {
  selfconfiguration=$(PGPASSWORD=$POSTGRES_PASSWORD psql -X -A \
    -h "$POSTGRES_HOST" -U "$POSTGRES_USER" "$POSTGRES_DB" -t -c \
    "SELECT COUNT(*) from self_configurations_selfconfiguration")

  if [ "$selfconfiguration" = "0" ]; then
    echo "No configuration. Initializing confirmation validator"

    echo "Waiting for PV..."
    until curl -f http://pv:8000/config > /dev/null 2>&1; do
      sleep 1
    done
    echo "PV started"

    /opt/project/manage.py initialize_validator \
      --node_identifier "$NODE_IDENTIFIER" \
      --account_number "$ACCOUNT_NUMBER" \
      --default_transaction_fee 1 \
      --daily_confirmation_rate 1 \
      --node_type CONFIRMATION_VALIDATOR \
      --protocol http \
      --ip_address "$PUBLIC_IP_ADDRESS" \
      --port "$NODE_PORT" \
      --root_account_file https://gist.githubusercontent.com/buckyroberts/395c946b33b9a458d677c919ae3f00b1/raw/55acc740cb25d2b4d02430f096b225e70677ec23/alpha-02.json \
      --version_number v1.0 \
      --unattended

    echo "Waiting for self..."
    until curl -f http://localhost:8000/config > /dev/null 2>&1; do
      sleep 1
    done
    echo "self started"

    /opt/project/manage.py set_primary_validator \
      --ip_address "$PUBLIC_IP_ADDRESS" \
      --port 8001 \
      --protocol http \
      --trust 100 \
      --unattended

    echo "Confirmation validator initialized"
  fi
}

if [ "$1" = "" ]; then
  /opt/project/manage.py migrate;
  init_node &
  /opt/project/manage.py runserver 0.0.0.0:8000;
else
  exec "$@"
fi
