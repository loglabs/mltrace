=========
Changelog
=========

- :release:`0.17 <2021-11-04>`
- :support:`-` Added ability to create tests and execute them before and after components are run. Also, the web app has a React Router refactor, thanks to `@Boyuan-Deng`.

  .. warning::
    This change is requries a DB migration. You can follow the documentation to perform the migration_ if you are using a release prior to this one.

- :feature:`226` Adds functionality to run triggers before and after components are run. Thanks `@aditim1359` for taking this on!


- :release:`0.16 <2021-07-08>`
- :support:`-` Added the review feature to aid in debugging erroneous outputs and functionality to log git tags to integrate with DVC.

  .. warning::
    This change is requries a DB migration. You can follow the documentation to perform the migration_ if you are using a release prior to this one.

- :feature:`178` Adds the review feature to allow users to flag problematic outputs and determine common component runs used in producing the outputs. See details here: :ref:`Reviewing tool`
- :feature:`176` Adds functionality to log git tags an example_ of how to use DVC with mltrace. Thanks `@jeannefukumaru` for taking this on!

- :release:`0.15 <2021-05-21>`
- :support:`-` Added CLI (command line utilities) and component run staleness features. 

  .. warning::
    This change is requries a DB migration. You can follow the documentation to perform the migration_ if you are using a release prior to this one.

- :feature:`76` Add a staleness feature to component runs to hint whether the component needs to be rerun. See details here: :ref:`Staleness Overview`
- :feature:`56` Adds CLI commands as an alternative to the UI. Thanks `@ariG23498` for taking this on! See documentation on how to use CLI here: :ref:`Using the CLI`


.. _migration: https://github.com/loglabs/mltrace/tree/master/mltrace/db/migrations
.. _example: https://github.com/loglabs/mltrace/tree/master/examples/dvc-mltrace