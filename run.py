<<<<<<< HEAD
from app import app
=======
from app import create_app

app = create_app()
>>>>>>> 94189477432845f0ef7129871895b9a3c08802c8

if __name__ == '__main__':
    app.run(debug=True)
