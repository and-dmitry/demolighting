==================================
demolighting - Django demo project
==================================

This is demo/toy web-application for controlling imaginary lamps.

* Administrator can create, delete and rename lamps via django-admin.
* Registered users can turn on/off lamps and change brightness via
  RESTful API at `/api/`.
* Working periods of lamps are saved to the database. These periods
  can be viewed via admin interface. Total working duration and
  timestamp of last switch are included in API representation of each
  lamp.

This project uses Django REST framework and SQLite. It is has no
production configuration (at least yet).

Prerequisites: Python 3.7, pipenv, httpie (to use the API)

.. code-block::

   cd demolighting/
   pipenv install --dev
   pipenv shell
   ./manage.py test
   ./manage.py createsuperuser
   ./manage.py runserver

   # Create lamps at http://127.0.0.1:8000/admin/
   # Go to http://127.0.0.1:8000/api/ to access the browsable API
   # Or use httpie, but create a token first (in admin interface)
   http get http://127.0.0.1:8000/api/ 'Authorization: Token YOUR_TOKEN'
