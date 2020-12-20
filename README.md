# Info

This service exists for those who need to get some kind of session lock or simple semaphore-like mechanism.

Actual case was absence of proper concurrency limit for [BitBucket Pipelines](https://jira.atlassian.com/browse/BCLOUD-12821).

# Usage

- `PUT https://getlock.tech/<uuid>`

  Create new lock or update existing one.

  Params:

  - `ttl` - float, in seconds, default is `60.0`.

- `GET https://getlock.tech/<uuid>`

  Check if lock is active, response code is 423 on active or 404 for other cases.

- `DELETE https://getlock.tech/<uuid>`

  Release existing lock.


## Example

Let's we have some task which takes up to 1 hour yet could be triggered from number of workers. It concurrency required to be limited to single worker at a time.

We choose some random yet valid [UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) as our job ID. It should be the same for all workers you decide to limit concurrency for:

```
MY_JOB_UUID=28c9c1be-7bb8-4e8c-b22e-c16402a421d5
```

Worker logic then could look like following:

```sh
echo "Checking if another job is running ..."

while ["$(curl https://getlock.tech/${SOME_UUID} | jq '.locked')" = "true"]; do
  echo "Locked, waiting for free spot ..."
  sleep 1
done

echo "Free spot found"

echo "Acquiring lock ..."

# NOTE Prefer lower TTL values while refreshing lock periodically
#   to not waste time in case job has failed
curl -X PUT -d ttl=$[60*60] https://getlock.tech/${SOME_UUID}

echo "Starting payload ..."

sleep 2400

echo "Payload done"

echo "Releasing lock ..."

curl -X DELETE https://getlock.tech/${SOME_UUID}

echo "Job done"
```

I also recommend you to consider using awesome [httpie](https://httpie.io/) tool.
