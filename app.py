import API
import logging

app = API.create_app(config_class=API.Config)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.run()
