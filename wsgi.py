from project import create_app

# File ini digunakan oleh Gunicorn untuk menemukan dan menjalankan instance aplikasi Flask.
# Gunicorn akan mencari variabel bernama 'app' di dalam file ini.
app = create_app()
