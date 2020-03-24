from app import app


@app.route('/')
def main():
    return 'Buenos dias globo!'
