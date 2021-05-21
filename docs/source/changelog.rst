=========
Changelog
=========

- :release:`0.14 <2021-05-21>`
- :support:`-` Added CLI (command line utilities) and component run staleness features. 

  .. warning::
    This change is requries a DB migration. You can follow the documentation to perform the migration_ if you are using a release prior to this one.

- :feature: `76` Add a staleness feature to component runs to hint whether the component needs to be rerun. See details here: :ref:`Staleness Overview`
- :feature: `56` Adds CLI commands as an alternative to the UI. Thanks `@ariG23498` for taking this on! See documentation on how to use CLI here: :ref:`Using the CLI`

.. _migration: https://github.com/loglabs/mltrace/tree/master/mltrace/db/migrations