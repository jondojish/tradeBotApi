# Setup

## Configure S3
* Create an S3 bucket with AWS and put it in your .env
* BUCKET_NAME={bucket name}
* Run the'aws configure' command and enter Aws Access Key ID, AWS Secret Acces Key and region name
* Set CORS for Bucket as -->
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
* Upload a file named 'id_log.txt' to Bucket

## Configure Api
* Create a .env file (is more secure than including in code)
* API_TOKEN=oanda api key/token
* ACCOUNT_ID=id of account to run program on

# Run
* Pass market(s) to the order.py file via command line
* e.g for windows: python order.py USD_JPY EUR_USD



