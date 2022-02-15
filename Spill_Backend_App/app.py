import sentry_sdk

from sentry_sdk.integrations.flask import FlaskIntegration

import API
import logging

sentry_sdk.init(
    dsn="https://14705234ea144f8ca9c07f5b60e96d4b@o1144439.ingest.sentry.io/6208485",
    integrations=[FlaskIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)


app = API.create_app(config_class=API.Config)
logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80)
