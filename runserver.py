from meetups import app as application

if __name__ == '__main__':
    application.run(
        debug=True,
        use_reloader=True,
    )
