# Purpose of Application

The primary objective of this application is to function as a fully
centralised repository in which users may deposit, catalogue and
retrieve Digital Humanities Objects (DHOs) from any remote location. At
its core, it rests upon a hardened Apache HTTP Server configured with
mod_wsgi to execute a Django-based web application; this combination has
been chosen to guarantee both high availability and the capacity to
scale seamlessly as demand grows. All DHOs, together with their
associated metadata, are stored in a relational database (MySQL) while
binary assets (including high-resolution stills, multi-plane image
stacks and PTM files) are managed via a secure media storage subsystem.\
Users interact with the system through a clean, intuitive Django web
interface that supports secure login, role-based permissions and
full-text searching across titles, descriptions, tags and custom
metadata fields. On the backend, Django's ORM and caching layers ensure
that queries remain performant even as the corpus expands, while
Apache's built-in security modules (SSL/TLS, HTTP authentication,
access-control lists) protect sensitive cultural heritage data in
transit and at rest. Administrators may perform routine maintenance
tasks---such as backing up the database, rotating log files and applying
security patches---directly from a command-line utility or via an
optional web-based dashboard.\
When a user elects to view a DHO that has been augmented with Polynomial
Texture Mapping (.ptm) files, the application dynamically constructs a
secure launch token and redirects to a page in which a WebGL-enabled RTI
(Reflectance Transformation Imaging) viewer is initialised. As each
image plane loads, the viewer assembles them into a single composite
surface representation. Once all layers are in place, the interface
presents a virtual light source widget: users may click and drag to vary
the direction, elevation and intensity of illumination in real time.
This interactive environment reveals minute surface topography---such as
tool-marks, inscriptions or weathering patterns---by accentuating how
light interacts with the object's micro-relief.\
In practical terms, this means that a scholar examining an ancient
inscription can sweep the light across the carving to make faint
lettering more legible, or that a conservator can simulate raking light
to identify cracks and surface anomalies. The viewer also offers
standard controls for zooming, panning, toggling wireframe overlays and
exporting annotated snapshots for publication or archiving.
Collectively, these features ensure that the application not only
centralises DHO storage but also delivers an immersive, research-grade
visualisation toolset for the global humanities community.

# Installation

## Hardware and Software Requirements

Ideally, this application should be deployed on a server-class machine
equipped with high-performance solid-state drives (SSDs) offering rapid
random-access read and write speeds, thereby ensuring swift retrieval
and storage of large digital humanities assets. A modern multi-core
processor---at a minimum a dual-core CPU with simultaneous
multithreading support---is strongly recommended to handle concurrent
user requests, background media processing tasks and real-time RTI
rendering without undue latency. In addition, we advise provision of at
least 16 GB of system memory to accommodate database caching, web server
operations and viewer workloads; a gigabit-capable network interface is
likewise advisable to facilitate responsive remote access, particularly
in scenarios involving high-resolution imagery or multiple simultaneous
sessions.\
On the software front, the application has been developed, tested and
optimised exclusively for a UNIX-based operating environment, with
Ubuntu LTS releases serving as the reference platform. Installation,
configuration scripts and continuous integration pipelines all presume
Ubuntu's package management, file-system hierarchy and
service-management conventions; consequently, deployment upon any other
distribution or flavour of UNIX or Linux is neither supported nor
guaranteed to function correctly. Users electing to install on alternate
systems do so entirely at their own risk and may encounter compatibility
issues with dependencies such as mod_wsgi, the Python interpreter,
system-level libraries (e.g. libjpeg, libtiff) or the chosen relational
database engine. We therefore recommend Ubuntu 22.04.05 LTS or later in
conjunction with the system's native APT repositories for seamless
installation, automated security updates and long-term maintenance.

## Required Libraries

When setting up the application in a local environment for testing
purposes, the sole prerequisite that must be manually installed is
MYSQL, which will be kept up to date after the initial install due to
the inclusion in the requirements.txt file. All other dependencies are
declared within the requirements.txt manifest and will be automatically
retrieved and installed upon the invocation of the web server. It is
therefore essential that the Python interpreter can locate and import
the following libraries without error:

1.  asgiref

2.  attrs

3.  beautifulsoup4

4.  behave

5.  behave-django

6.  certifi

7.  cffi

8.  charset-normalizer

9.  crispy-bootstrap4

10. Django

11. django-crispy-forms

12. django-froala-editor

13. flake8

14. h11

15. idna

16. mccabe

17. mysqlclient

18. outcome

19. packaging

20. parse

21. parse-type

22. pillow

23. pycodestyle

24. pycparser

25. pyflakes

26. pymysql

27. PySocks

28. python-dotenv

29. pytz

30. requests

31. selenium

32. six

33. sniffio

34. sortedcontainers

35. soupsieve

36. sqlparse

37. trio

38. trio-websocket

39. typing_extensions

40. tzdata

41. urllib3

42. webdriver-manager

43. websocket-client

44. whitenoise

45. wsproto

Provided that pip itself is up to date, executing the server start-up
command will ensure that each of these modules is installed at the
specified version noted in requirements.txt, simplifying the local
deployment and aligning it with the production configuration.

## Database Setup

Once MYSQL is installed you will need to setup a table with the
provided.

In order to do this follow these steps:

1.  On the command line navigate to the top most directory of the
    project if you are not there already

2.  cd into the websiteDatabase directory

3.  Run the command mysql -u ADMIN -p websiteDatabase \<schema.sql

To test it worked and setup was successful follow these steps on the
command line:

1.  run: mysql -u ADMIN -p

2.  next enter: USE websiteDatabase;

3.  followed by: SHOW TABLES;

4.  finally input: DESCRIBE TABLES;

After you have completed these steps you have installation

# Deploying the Application Locally & Testing 

## Deployment

In order to deploy the application locally all one needs to do on is run
these steps on the command line:

1.  Navigate to the top directory of the project

2.  Run sudo vi djangoBackend/settings.py

3.  Navigate down to the DEBUG = False line and change it to DEBUG =
    True

4.  Further navigate down to the SSL section and comment out line 37-42
    thats SECURE_SSL_REDIRECT = True down to SECURE_CONTENT_TYPE_NOSNIFF
    = True

5.  Run this command only changing python to python3 if that is how your
    PATH variable are setup: python manage.py createsuperuser

6.  When prompted enter a username and password for your local admin
    account

7.  Run the following command : python manage.py runserver

8.  Open a web browser and navigate to 127.0.0.1:8000

## Deployed Version Non-Local

To access a deployed instance of this project for demonstration or testing purposes, please visit the following link: https://sbx-hotel-srv1.abdn.ac.uk

## How to Test

To verify the functionality of the application and ensure that all core
features perform as expected, a comprehensive suite of automated tests
has been included. Executing these tests is straightforward and can be
accomplished through a single command issued via the command line
interface.\
By running the command python manage.py test, Django will automatically
discover and execute all test cases defined within the homepage/tests
directory. At present, there are approximately 52 distinct tests
included, covering a wide range of the application's functionality.
Provided the system is correctly configured and all dependencies are in
place, these tests should execute successfully on the first attempt
without error.

# Extending the Application

This application is designed to be flexible and modular, allowing
developers to extend its functionality to meet specific needs. Below are
the guidelines and recommendations for extending the system:

## Understanding the Project Structure

Before adding new features, it is essential to familiarise yourself with
the project's structure. The primary components of the system include
the following:

- Models: Responsible for defining the database schema.

- Views: Handle the logic for processing requests and returning
  responses.

- Templates: Manage the presentation and layout of content.

- URLs: Define the routing of different parts of the application.

## Adding New Models

If your extension requires new data storage, you can define new models
in the relevant models.py file. To add a new model, follow these steps:

- Create a new class that inherits from django.db.models.Model.

- Define the fields you need for your model.

- Run python manage.py makemigrations to generate migration files.

- Apply migrations using python manage.py migrate.

## Modifying Views and Templates

If your extension requires new pages or changes to existing pages:

- Add a new view in the views.py file. This could be a class-based or
  function-based view depending on the complexity.

- Update the relevant template files to support the new features.

- Ensure that the new views are mapped in the urls.py file.

## Integrating with External APIs or Services

The system can be extended by integrating with third-party APIs or
services. To do so:

- Install necessary libraries (e.g., requests, django-rest-framework).

- Add the API interaction code in the relevant view or service layer.

- Ensure appropriate error handling is implemented for external
  requests.

- Create helper functions or services to encapsulate API calls and
  responses.

## Adding New User Roles and Permissions

If your extension requires specific access control:

- You can extend the default User model or use Django's permission
  system to manage user roles and access.

- Define custom permissions in models.py or through Django's admin
  interface.

- Ensure that views and templates are restricted based on user
  permissions.

## Testing Your Extension

For a robust extension, it is essential to add appropriate tests. Django
provides a testing framework to facilitate the creation of automated
tests:

- Add test cases for your new functionality in the tests.py file within
  the relevant app directory.

- Use Django's built-in test client to simulate user interactions and
  check if the new feature works as expected.

- Run the tests with python manage.py test to ensure the system behaves
  as intended.

## Deployment Considerations

After implementing new features, you may need to update the deployment
configuration:

- Modify your settings to support new environment variables or
  configurations.

- If your extension involves static files, ensure that they are properly
  handled in production (using collectstatic).

- If using a database change, ensure that migrations are correctly
  handled during deployment.

## Documentation and Code Quality

When extending the system, always ensure:

- Code is well-documented, with clear comments and docstrings explaining
  the logic.

- Adherence to Django's coding conventions and PEP 8.

- Proper version control practices are followed, ensuring all changes
  are tracked with descriptive commit messages.

By following these guidelines, you can effectively extend the system
while maintaining maintainability, scalability, and security. Always
test thoroughly and ensure your extensions integrate seamlessly with the
existing codebase.
