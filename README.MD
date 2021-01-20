# Setup

## Configure S3
* Create a user on AWS via IAM with 'AmazonS3FullAccess' permissions
* Create an S3 bucket with AWS
* Set CORS for Bucket as:

    ```
    [
        {
            "AllowedHeaders": [
                "*"
            ],
            "AllowedMethods": [
                "POST",
                "GET",
                "PUT"
            ],
            "AllowedOrigins": [
                "*"
            ],
            "ExposeHeaders": []
        }
    ]
    ```
* Upload an empty file named 'id_log.txt' to Bucket

## Configure
* Put in .env for windows, and config vars for heroku

    ```
    API_TOKEN={oanda api key/token}
    ACCOUNT_ID={id of account to run program on}

    AWS_BUCKET_NAME={S3 bucket name}
    AWS_ACCESS_KEY_ID={your aws access key id}
    AWS_SECRET_ACCESS_KEY={your aws secret access key id}
    ```


## Run
* Pass market(s) to the order.py file via command line
* E.g for windows

    ```
    python order.py USD_JPY EUR_USD
    ```

# Heroku
* Look at 'configure S3' first as you will need to create an S3 bucket
* ## config vars
    * Look at Configure
* ## running the script
    * First deploy the script to heroku
    * Run the script like this

        ```heroku ps:scale worker=1```
    * This runs the main.py as specified in Procfile, the "1" specifies the amount of workers that will run
    * You can check logs like this

        ```heroku logs --tail```
    * You can stop the script by scaling down the amount of workers like this

        ```heroku ps:scale worker=0```



