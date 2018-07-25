#!venv/bin/python
"""
Use this script to run flask locally
"""
if __name__ == "__main__":
    from app import app
    app.run(debug=True, host='0.0.0.0')
