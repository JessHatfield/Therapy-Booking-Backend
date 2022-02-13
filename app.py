import API

app = API.create_app(config_class=API.Config)


if __name__ == "__main__":
    app.run()
